# tests/test_service.py
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import json
import sys
from pvv_mcp_server import mod_service


class TestSpeakTool:
    """speak tool関数のユニットテスト"""

    @pytest.mark.asyncio
    @patch('pvv_mcp_server.mod_service.mod_speak.speak')
    async def test_speak_normal_case(self, mock_speak):
        """正常系: デフォルトパラメータでの音声合成"""
        # Arrange
        style_id = 1
        msg = "こんにちは"
        
        # Act
        result = await mod_service.speak(style_id, msg)
        
        # Assert
        mock_speak.assert_called_once_with(
            style_id=style_id,
            msg=msg,
            speedScale=1.0,
            pitchScale=0.0,
            intonationScale=1.0,
            volumeScale=1.0
        )
        assert "音声合成・再生が完了しました" in result
        assert f"style_id={style_id}" in result
        assert f"msg='{msg}'" in result

    @pytest.mark.asyncio
    @patch('pvv_mcp_server.mod_service.mod_speak.speak')
    async def test_speak_with_custom_parameters(self, mock_speak):
        """正常系: カスタムパラメータでの音声合成"""
        # Arrange
        style_id = 2
        msg = "テスト"
        speed = 1.5
        pitch = 0.3
        intonation = 1.2
        volume = 0.8
        
        # Act
        result = await mod_service.speak(
            style_id, msg, 
            speedScale=speed, 
            pitchScale=pitch,
            intonationScale=intonation,
            volumeScale=volume
        )
        
        # Assert
        mock_speak.assert_called_once_with(
            style_id=style_id,
            msg=msg,
            speedScale=speed,
            pitchScale=pitch,
            intonationScale=intonation,
            volumeScale=volume
        )
        assert "音声合成・再生が完了しました" in result

    @pytest.mark.asyncio
    @patch('pvv_mcp_server.mod_service.mod_speak.speak')
    async def test_speak_error_case(self, mock_speak):
        """異常系: mod_speak.speakでエラーが発生"""
        # Arrange
        style_id = 1
        msg = "エラーテスト"
        mock_speak.side_effect = Exception("API connection failed")
        
        # Act
        result = await mod_service.speak(style_id, msg)
        
        # Assert
        assert "エラーが発生しました" in result
        assert "API connection failed" in result


class TestSpeakMetanAskaTool:
    """speak_metan_aska tool関数のユニットテスト"""

    @pytest.mark.asyncio
    @patch('pvv_mcp_server.mod_service.mod_speak_metan_aska.speak_metan_aska')
    async def test_speak_metan_aska_normal_case(self, mock_speak_metan_aska):
        """正常系: アスカとして発話"""
        # Arrange
        msg = "あんた、バカぁ！"
        
        # Act
        result = await mod_service.speak_metan_aska(msg)
        
        # Assert
        mock_speak_metan_aska.assert_called_once_with(msg)
        assert "発話完了" in result
        assert msg in result

    @pytest.mark.asyncio
    @patch('pvv_mcp_server.mod_service.mod_speak_metan_aska.speak_metan_aska')
    async def test_speak_metan_aska_error_case(self, mock_speak_metan_aska):
        """異常系: 発話エラー"""
        # Arrange
        msg = "エラーテスト"
        mock_speak_metan_aska.side_effect = Exception("Voice synthesis failed")
        
        # Act
        result = await mod_service.speak_metan_aska(msg)
        
        # Assert
        assert "エラー" in result
        assert "Voice synthesis failed" in result


class TestSpeakersResource:
    """speakers resource関数のユニットテスト"""

    @patch('pvv_mcp_server.mod_service.mod_speakers.speakers')
    def test_speakers_normal_case(self, mock_speakers):
        """正常系: 話者一覧の取得"""
        # Arrange
        mock_speakers.return_value = [
            {"name": "四国めたん", "speaker_uuid": "uuid1"},
            {"name": "ずんだもん", "speaker_uuid": "uuid2"}
        ]
        
        # Act
        result = mod_service.speakers()
        
        # Assert
        mock_speakers.assert_called_once()
        data = json.loads(result)
        assert len(data) == 2
        assert data[0]["name"] == "四国めたん"
        assert data[1]["name"] == "ずんだもん"

    @patch('pvv_mcp_server.mod_service.mod_speakers.speakers')
    def test_speakers_empty_list(self, mock_speakers):
        """正常系: 話者が空の場合"""
        # Arrange
        mock_speakers.return_value = []
        
        # Act
        result = mod_service.speakers()
        
        # Assert
        data = json.loads(result)
        assert data == []

    @patch('pvv_mcp_server.mod_service.mod_speakers.speakers')
    def test_speakers_error_case(self, mock_speakers):
        """異常系: 話者一覧取得エラー"""
        # Arrange
        mock_speakers.side_effect = Exception("API error")
        
        # Act
        result = mod_service.speakers()
        
        # Assert
        assert "エラー" in result
        assert "API error" in result


class TestSpeakerInfoResource:
    """speaker_info resource関数のユニットテスト"""

    @patch('pvv_mcp_server.mod_service.mod_speaker_info.speaker_info')
    def test_speaker_info_normal_case(self, mock_speaker_info):
        """正常系: 話者情報の取得"""
        # Arrange
        speaker_id = "四国めたん"
        mock_speaker_info.return_value = {
            "name": "四国めたん",
            "speaker_uuid": "uuid1",
            "styles": [
                {"name": "ノーマル", "id": 2}
            ]
        }
        
        # Act
        result = mod_service.speaker_info(speaker_id)
        
        # Assert
        mock_speaker_info.assert_called_once_with(speaker_id)
        data = json.loads(result)
        assert data["name"] == "四国めたん"
        assert len(data["styles"]) == 1

    @patch('pvv_mcp_server.mod_service.mod_speaker_info.speaker_info')
    def test_speaker_info_by_uuid(self, mock_speaker_info):
        """正常系: UUIDで話者情報を取得"""
        # Arrange
        speaker_uuid = "uuid123"
        mock_speaker_info.return_value = {
            "name": "ずんだもん",
            "speaker_uuid": speaker_uuid
        }
        
        # Act
        result = mod_service.speaker_info(speaker_uuid)
        
        # Assert
        mock_speaker_info.assert_called_once_with(speaker_uuid)
        data = json.loads(result)
        assert data["speaker_uuid"] == speaker_uuid

    @patch('pvv_mcp_server.mod_service.mod_speaker_info.speaker_info')
    def test_speaker_info_error_case(self, mock_speaker_info):
        """異常系: 話者情報取得エラー"""
        # Arrange
        speaker_id = "存在しない話者"
        mock_speaker_info.side_effect = Exception("Speaker not found")
        
        # Act
        result = mod_service.speaker_info(speaker_id)
        
        # Assert
        assert "エラー" in result
        assert "Speaker not found" in result


class TestStartFunctions:
    """start関数群のユニットテスト"""

    @patch('pvv_mcp_server.mod_service.start_mcp_avatar')
    @patch('pvv_mcp_server.mod_service.start_mcp_avatar_disabled')
    def test_start_with_avatar_enabled(self, mock_disabled, mock_enabled):
        """正常系: アバター有効で起動"""
        # Arrange
        conf = {
            "avatar": {
                "enabled": True,
                "image_path": "/path/to/image"
            }
        }
        
        # Act
        mod_service.start(conf)
        
        # Assert
        mock_enabled.assert_called_once_with(conf["avatar"])
        mock_disabled.assert_not_called()

    @patch('pvv_mcp_server.mod_service.start_mcp_avatar')
    @patch('pvv_mcp_server.mod_service.start_mcp_avatar_disabled')
    def test_start_with_avatar_disabled(self, mock_disabled, mock_enabled):
        """正常系: アバター無効で起動"""
        # Arrange
        conf = {
            "avatar": {
                "enabled": False
            }
        }
        
        # Act
        mod_service.start(conf)
        
        # Assert
        mock_disabled.assert_called_once_with(conf["avatar"])
        mock_enabled.assert_not_called()

    @patch('pvv_mcp_server.mod_service.start_mcp_avatar')
    @patch('pvv_mcp_server.mod_service.start_mcp_avatar_disabled')
    def test_start_without_avatar_config(self, mock_disabled, mock_enabled):
        """正常系: avatar設定なしで起動"""
        # Arrange
        conf = {}
        
        # Act
        mod_service.start(conf)
        
        # Assert
        # avatar設定がない場合、get()でNoneが返るのでdisabledが呼ばれる
        mock_disabled.assert_called_once()

    @patch('pvv_mcp_server.mod_service.pvv_mcp_server.mod_avatar_manager.setup')
    @patch('pvv_mcp_server.mod_service.mcp.run')
    def test_start_mcp_avatar_disabled(self, mock_mcp_run, mock_setup):
        """正常系: start_mcp_avatar_disabled関数のテスト"""
        # Arrange
        conf = {"enabled": False}
        
        # Act
        mod_service.start_mcp_avatar_disabled(conf)
        
        # Assert
        mock_setup.assert_called_once_with(conf)
        mock_mcp_run.assert_called_once_with(transport="stdio")

    @patch('pvv_mcp_server.mod_service.mcp.run')
    def test_start_mcp(self, mock_mcp_run):
        """正常系: start_mcp関数のテスト"""
        # Arrange
        conf = {"test": "config"}
        
        # Act
        mod_service.start_mcp(conf)
        
        # Assert
        mock_mcp_run.assert_called_once_with(transport="stdio")

    @patch('pvv_mcp_server.mod_service.QApplication')
    @patch('pvv_mcp_server.mod_service.pvv_mcp_server.mod_avatar_manager.setup')
    @patch('pvv_mcp_server.mod_service.Thread')
    @patch('pvv_mcp_server.mod_service.sys.exit')
    def test_start_mcp_avatar(self, mock_exit, mock_thread, mock_setup, mock_qapp):
        """正常系: start_mcp_avatar関数のテスト"""
        # Arrange
        conf = {"enabled": True}
        mock_app_instance = Mock()
        mock_qapp.return_value = mock_app_instance
        mock_app_instance.exec.return_value = 0
        
        # Act
        mod_service.start_mcp_avatar(conf)
        
        # Assert
        # スレッドが起動される
        mock_thread.assert_called_once()
        thread_call = mock_thread.call_args
        assert thread_call[1]["target"] == mod_service.start_mcp
        assert thread_call[1]["args"] == (conf,)
        assert thread_call[1]["daemon"] is True
        
        # QApplicationが作成される
        mock_qapp.assert_called_once()
        
        # アバターマネージャがセットアップされる
        mock_setup.assert_called_once_with(conf)
        
        # アプリケーションが実行される
        mock_app_instance.exec.assert_called_once()
        mock_exit.assert_called_once_with(0)