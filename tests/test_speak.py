import unittest
from unittest.mock import patch, MagicMock
import numpy as np


class TestSpeak(unittest.TestCase):
    """
    mod_speak.speak() の単体テスト
    """

    @patch("pvv_mcp_server.mod_speak.sf.read")
    @patch("pvv_mcp_server.mod_speak.sd.OutputStream")
    @patch("pvv_mcp_server.mod_avatar_manager")
    @patch("pvv_mcp_server.mod_speak.requests.post")
    def test_speak_normal(self, mock_post, mock_avatar, mock_sd_stream, mock_sf_read):
        """正常系: speak() が口パク→立ち絵の順に呼ばれる"""
        # --- ダミーのレスポンス設定 ---
        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"speedScale": 1}),
            MagicMock(status_code=200, content=b"dummy_wav_data"),
        ]

        # 音声データとサンプリングレートをモック
        mock_sf_read.return_value = (np.zeros((100, 1), dtype=np.float32), 24000)

        # OutputStream のモック（with文対応）
        mock_stream_instance = MagicMock()
        mock_sd_stream.return_value.__enter__.return_value = mock_stream_instance

        # --- 実行 ---
        from pvv_mcp_server import mod_speak
        mod_speak.speak(1, "テストです")

        # --- 呼び出し確認 ---
        actual_calls = [call.args for call in mock_avatar.set_anime_type.call_args_list]
        expected_calls = [
            (1, "口パク"),
            (1, "立ち絵")
        ]
        self.assertEqual(actual_calls, expected_calls)

    # ================================================================
    # 例外系テスト
    # ================================================================

    @patch("pvv_mcp_server.mod_speak.requests.post")
    def test_speak_audio_query_error(self, mock_post):
        """異常系: audio_query が失敗する場合"""
        mock_post.side_effect = Exception("Connection error")

        from pvv_mcp_server import mod_speak
        with self.assertRaises(Exception) as cm:
            mod_speak.speak(1, "テスト")
        self.assertIn("VOICEVOX API通信エラー", str(cm.exception))

    @patch("pvv_mcp_server.mod_speak.sf.read")
    @patch("pvv_mcp_server.mod_speak.sd.OutputStream")
    @patch("pvv_mcp_server.mod_avatar_manager")
    @patch("pvv_mcp_server.mod_speak.requests.post")
    def test_speak_audio_playback_error(self, mock_post, mock_avatar, mock_sd_stream, mock_sf_read):
        """異常系: 再生処理中にエラーが発生する"""
        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"speedScale": 1}),
            MagicMock(status_code=200, content=b"dummy_wav_data"),
        ]
        mock_sf_read.side_effect = Exception("再生エラー")

        from pvv_mcp_server import mod_speak
        with self.assertRaises(Exception) as cm:
            mod_speak.speak(1, "テスト")
        self.assertIn("音声再生エラー", str(cm.exception))

    def test_remove_bracket_text(self):
        """remove_bracket_text() の単体テスト"""
        from pvv_mcp_server.mod_speak import remove_bracket_text
        self.assertEqual(remove_bracket_text("これは（テスト）です"), "これはです")
        self.assertEqual(remove_bracket_text("これは(テスト)です"), "これはです")
        self.assertEqual(remove_bracket_text("（ああ）(いい)うう"), "うう")
        self.assertEqual(remove_bracket_text("（なし）"), "")


if __name__ == "__main__":
    unittest.main()
