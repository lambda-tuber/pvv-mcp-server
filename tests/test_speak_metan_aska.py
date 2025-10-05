import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import io
import soundfile as sf
from pvv_mcp_server.mod_speak_metan_aska import speak_metan_aska


class TestSpeakMetanAska(unittest.TestCase):

    @patch('pvv_mcp_server.mod_speak_metan_aska.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak_metan_aska.requests.post')
    def test_speak_metan_aska_success(self, mock_post, mock_outputstream):
        """正常系：音声合成と再生が正しく行われることを確認"""

        # audio_query のレスポンス
        mock_query_response = MagicMock()
        mock_query_response.json.return_value = {"accent_phrases": []}
        mock_query_response.raise_for_status.return_value = None

        # synthesis のレスポンス（WAVデータ生成）
        wav_bytes_io = io.BytesIO()
        sf.write(wav_bytes_io, np.zeros((10, 1), dtype=np.float32), 24000, format='WAV')
        wav_bytes = wav_bytes_io.getvalue()

        mock_synthesis_response = MagicMock()
        mock_synthesis_response.content = wav_bytes
        mock_synthesis_response.raise_for_status.return_value = None

        # post の戻り値を設定
        mock_post.side_effect = [mock_query_response, mock_synthesis_response]

        # OutputStream のモック設定
        mock_stream = MagicMock()
        mock_outputstream.return_value.__enter__.return_value = mock_stream

        # 関数実行
        speak_metan_aska("テストメッセージ")

        # 検証
        self.assertEqual(mock_post.call_count, 2)

        # audio_query 呼び出し
        first_call = mock_post.call_args_list[0]
        self.assertIn('audio_query', first_call[0][0])
        self.assertEqual(first_call[1]['params']['text'], "テストメッセージ")
        self.assertEqual(first_call[1]['params']['speaker'], 6)

        # synthesis 呼び出し
        second_call = mock_post.call_args_list[1]
        self.assertIn('synthesis', second_call[0][0])
        self.assertEqual(second_call[1]['params']['speaker'], 6)

        # OutputStream が呼ばれたか確認
        mock_outputstream.assert_called_once()
        mock_stream.write.assert_called_once()

    @patch('pvv_mcp_server.mod_speak_metan_aska.requests.post')
    def test_speak_metan_aska_query_error(self, mock_post):
        """異常系：audio_query APIがエラーを返す場合"""

        # モックの設定：HTTPエラーを発生させる
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_post.return_value = mock_response

        # 例外が発生することを確認
        with self.assertRaises(Exception):
            speak_metan_aska("テストメッセージ")

    @patch('pvv_mcp_server.mod_speak_metan_aska.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak_metan_aska.requests.post')
    def test_speak_metan_aska_empty_message(self, mock_post, mock_outputstream):
        """境界値テスト：空文字列のメッセージ"""

        # audio_query のレスポンス
        mock_query_response = MagicMock()
        mock_query_response.json.return_value = {"accent_phrases": []}
        mock_query_response.raise_for_status.return_value = None

        # synthesis のレスポンス（空データ）
        wav_bytes_io = io.BytesIO()
        sf.write(wav_bytes_io, np.zeros((0, 1), dtype=np.float32), 24000, format='WAV')
        wav_bytes = wav_bytes_io.getvalue()

        mock_synthesis_response = MagicMock()
        mock_synthesis_response.content = wav_bytes
        mock_synthesis_response.raise_for_status.return_value = None

        mock_post.side_effect = [mock_query_response, mock_synthesis_response]

        # OutputStream のモック
        mock_stream = MagicMock()
        mock_outputstream.return_value.__enter__.return_value = mock_stream

        # 実行（例外が出ないことを確認）
        try:
            speak_metan_aska("")
        except Exception as e:
            self.fail(f"Empty message should not raise exception: {e}")


if __name__ == '__main__':
    unittest.main()
