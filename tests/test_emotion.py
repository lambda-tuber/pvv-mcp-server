import unittest
from unittest.mock import patch, MagicMock
import logging

# テスト対象モジュールをインポート
import pvv_mcp_server.mod_emotion as mod_emotion


class TestEmotion(unittest.TestCase):
    def setUp(self):
        # 各テスト前にロガーを設定
        self.logger_patch = patch.object(mod_emotion, "logger")
        self.mock_logger = self.logger_patch.start()

        # モック avatar_manager
        self.avatar_patch = patch("pvv_mcp_server.mod_avatar_manager.set_anime_type")
        self.mock_set_anime_type = self.avatar_patch.start()

    def tearDown(self):
        self.logger_patch.stop()
        self.avatar_patch.stop()

    def test_emotion_normal(self):
        """正常に emotion() が呼ばれ、set_anime_type が呼び出される"""
        style_id = 1
        emotion = "えがお"

        mod_emotion.emotion(style_id, emotion)

        # 呼び出し確認
        self.mock_set_anime_type.assert_called_once_with(style_id, emotion)

        # ログ出力確認
        self.mock_logger.info.assert_any_call(f"emotion called. {style_id}, {emotion}")
        self.mock_logger.info.assert_any_call("emotion_metan_aska finalize")

    def test_emotion_exception(self):
        """set_anime_type が例外を投げた場合に emotion() が再スローする"""
        self.mock_set_anime_type.side_effect = RuntimeError("mock error")

        with self.assertRaises(Exception) as cm:
            mod_emotion.emotion(2, "びっくり")

        # エラーメッセージ確認
        self.assertIn("emotion error mock error", str(cm.exception))

        # 警告ログ確認
        self.mock_logger.warning.assert_called_once()
        self.mock_logger.info.assert_any_call("emotion_metan_aska finalize")

    def test_emotion_finally_always_runs(self):
        """例外が発生しても finalize ログが必ず呼ばれる"""
        self.mock_set_anime_type.side_effect = Exception("forced error")

        try:
            mod_emotion.emotion(5, "いかり")
        except Exception:
            pass

        # finalizeログは必ず呼ばれる
        self.mock_logger.info.assert_any_call("emotion_metan_aska finalize")


if __name__ == "__main__":
    unittest.main()
