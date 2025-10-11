# test_speak_metan_aska.py

import unittest
from unittest.mock import patch, MagicMock, mock_open
import io
import numpy as np
import pvv_mcp_server.mod_speak_metan_aska as mod_speak_metan_aska


class TestSpeakMetanAska(unittest.TestCase):
    """mod_speak_metan_aska.speak_metan_aska関数のテストクラス"""

    @patch('pvv_mcp_server.mod_speak_metan_aska.pvv_mcp_server.mod_avatar_manager.set_anime_key')
    @patch('pvv_mcp_server.mod_speak_metan_aska.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak_metan_aska.sf.read')
    @patch('pvv_mcp_server.mod_speak_metan_aska.requests.post')
    def test_speak_metan_aska_success(self, mock_post, mock_sf_read, mock_output_stream, mock_set_anime_key):
        """正常系: 音声合成と再生が成功するケース"""
        # モックの設定
        # audio_queryのレスポンス
        mock_query_response = MagicMock()
        mock_query_response.json.return_value = {"query": "data"}
        mock_query_response.raise_for_status = MagicMock()
        
        # synthesisのレスポンス
        mock_synthesis_response = MagicMock()
        mock_synthesis_response.content = b"audio_data"
        mock_synthesis_response.raise_for_status = MagicMock()
        
        # requests.postの戻り値を設定(1回目: query, 2回目: synthesis)
        mock_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        # soundfile.readのモック(サンプル音声データ)
        audio_data = np.array([[0.1, 0.1], [0.2, 0.2]], dtype=np.float32)
        samplerate = 24000
        mock_sf_read.return_value = (audio_data, samplerate)
        
        # OutputStreamのモック
        mock_stream = MagicMock()
        mock_output_stream.return_value.__enter__.return_value = mock_stream
        
        # テスト実行
        mod_speak_metan_aska.speak_metan_aska("テストメッセージ")
        
        # 検証
        # audio_queryが正しく呼ばれたか
        self.assertEqual(mock_post.call_count, 2)
        first_call = mock_post.call_args_list[0]
        self.assertEqual(first_call[0][0], "http://127.0.0.1:50021/audio_query")
        self.assertEqual(first_call[1]['params']['text'], "テストメッセージ")
        self.assertEqual(first_call[1]['params']['speaker'], 6)
        
        # synthesisが正しく呼ばれたか
        second_call = mock_post.call_args_list[1]
        self.assertEqual(second_call[0][0], "http://127.0.0.1:50021/synthesis")
        self.assertEqual(second_call[1]['params']['speaker'], 6)
        self.assertEqual(second_call[1]['json'], {"query": "data"})
        
        # soundfile.readが呼ばれたか
        mock_sf_read.assert_called_once()
        
        # 音声ストリームに書き込まれたか
        mock_stream.write.assert_called_once_with(audio_data)
        
        # アニメーションキーが設定されたか(開始時の口パクとfinallyでの待ち絵)
        self.assertEqual(mock_set_anime_key.call_count, 2)
        # 1回目: 口パク開始
        self.assertEqual(mock_set_anime_key.call_args_list[0][0], (6, "口パク"))
        # 2回目: finally で待ち絵に戻る

    @patch('pvv_mcp_server.mod_speak_metan_aska.pvv_mcp_server.mod_avatar_manager.set_anime_key')
    @patch('pvv_mcp_server.mod_speak_metan_aska.requests.post')
    def test_speak_metan_aska_query_error(self, mock_post, mock_set_anime_key):
        """異常系: audio_queryでエラーが発生するケース"""
        # モックの設定
        mock_query_response = MagicMock()
        mock_query_response.raise_for_status.side_effect = Exception("Query Error")
        mock_post.return_value = mock_query_response
        
        # テスト実行と検証
        with self.assertRaises(Exception) as context:
            mod_speak_metan_aska.speak_metan_aska("テストメッセージ")
        
        self.assertIn("Query Error", str(context.exception))

    @patch('pvv_mcp_server.mod_speak_metan_aska.pvv_mcp_server.mod_avatar_manager.set_anime_key')
    @patch('pvv_mcp_server.mod_speak_metan_aska.requests.post')
    def test_speak_metan_aska_synthesis_error(self, mock_post, mock_set_anime_key):
        """異常系: synthesisでエラーが発生するケース"""
        # モックの設定
        # audio_queryのレスポンス(成功)
        mock_query_response = MagicMock()
        mock_query_response.json.return_value = {"query": "data"}
        mock_query_response.raise_for_status = MagicMock()
        
        # synthesisのレスポンス(失敗)
        mock_synthesis_response = MagicMock()
        mock_synthesis_response.raise_for_status.side_effect = Exception("Synthesis Error")
        
        mock_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        # テスト実行と検証
        with self.assertRaises(Exception) as context:
            mod_speak_metan_aska.speak_metan_aska("テストメッセージ")
        
        self.assertIn("Synthesis Error", str(context.exception))

    @patch('pvv_mcp_server.mod_speak_metan_aska.pvv_mcp_server.mod_avatar_manager.set_anime_key')
    @patch('pvv_mcp_server.mod_speak_metan_aska.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak_metan_aska.sf.read')
    @patch('pvv_mcp_server.mod_speak_metan_aska.requests.post')
    def test_speak_metan_aska_audio_playback_error(self, mock_post, mock_sf_read, mock_output_stream, mock_set_anime_key):
        """異常系: 音声再生でエラーが発生するケース(finallyで待ち絵に戻る)"""
        # モックの設定
        mock_query_response = MagicMock()
        mock_query_response.json.return_value = {"query": "data"}
        mock_query_response.raise_for_status = MagicMock()
        
        mock_synthesis_response = MagicMock()
        mock_synthesis_response.content = b"audio_data"
        mock_synthesis_response.raise_for_status = MagicMock()
        
        mock_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        # soundfile.readでエラー発生
        mock_sf_read.side_effect = Exception("Audio Read Error")
        
        # テスト実行と検証
        with self.assertRaises(Exception) as context:
            mod_speak_metan_aska.speak_metan_aska("テストメッセージ")
        
        self.assertIn("音声再生エラー: Audio Read Error", str(context.exception))
        
        # tryブロックで口パク設定、finallyブロックで待ち絵に戻される
        self.assertEqual(mock_set_anime_key.call_count, 2)
        # 1回目: 口パク開始
        self.assertEqual(mock_set_anime_key.call_args_list[0][0], (6, "口パク"))
        # 2回目: finally で待ち絵に戻る


if __name__ == '__main__':
    unittest.main()