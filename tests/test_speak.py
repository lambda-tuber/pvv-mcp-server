# tests/test_speak.py
import pytest
from unittest.mock import Mock, MagicMock, patch, call
import io
import numpy as np
from pvv_mcp_server.mod_speak import speak


class TestSpeak:
    """speak関数のユニットテスト"""

    @patch('pvv_mcp_server.mod_speak.pvv_mcp_server.mod_avatar_manager.set_anime_key')
    @patch('pvv_mcp_server.mod_speak.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak.sf.read')
    @patch('pvv_mcp_server.mod_speak.requests.post')
    def test_speak_normal_case(self, mock_requests_post, mock_sf_read, mock_output_stream, mock_set_anime_key):
        """正常系: デフォルトパラメータでの音声合成と再生"""
        # Arrange
        style_id = 1
        msg = "こんにちは"
        
        # requestsのモック設定
        mock_query_response = Mock()
        mock_query_response.json.return_value = {
            "speedScale": 1.0,
            "pitchScale": 0.0,
            "intonationScale": 1.0,
            "volumeScale": 1.0
        }
        mock_query_response.raise_for_status = Mock()
        
        mock_synthesis_response = Mock()
        mock_synthesis_response.content = b"dummy_audio_data"
        mock_synthesis_response.raise_for_status = Mock()
        
        mock_requests_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        # soundfileのモック設定
        dummy_audio = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        mock_sf_read.return_value = (dummy_audio, 24000)
        
        # sounddeviceのモック設定
        mock_stream = MagicMock()
        mock_output_stream.return_value.__enter__.return_value = mock_stream
        
        # Act
        speak(style_id, msg)
        
        # Assert
        # audio_query APIの呼び出し確認
        assert mock_requests_post.call_count == 2
        first_call = mock_requests_post.call_args_list[0]
        assert first_call[0][0] == "http://localhost:50021/audio_query"
        assert first_call[1]["params"]["text"] == msg
        assert first_call[1]["params"]["speaker"] == style_id
        
        # synthesis APIの呼び出し確認
        second_call = mock_requests_post.call_args_list[1]
        assert second_call[0][0] == "http://localhost:50021/synthesis"
        assert second_call[1]["params"]["speaker"] == style_id
        
        # アニメーションキーの設定確認
        assert mock_set_anime_key.call_count == 2
        mock_set_anime_key.assert_any_call(style_id, "口パク")
        mock_set_anime_key.assert_any_call(style_id, "立ち絵")
        
        # 音声再生確認
        mock_sf_read.assert_called_once()
        mock_stream.write.assert_called_once()

    @patch('pvv_mcp_server.mod_speak.pvv_mcp_server.mod_avatar_manager.set_anime_key')
    @patch('pvv_mcp_server.mod_speak.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak.sf.read')
    @patch('pvv_mcp_server.mod_speak.requests.post')
    def test_speak_with_custom_parameters(self, mock_requests_post, mock_sf_read, mock_output_stream, mock_set_anime_key):
        """正常系: カスタムパラメータでの音声合成"""
        # Arrange
        style_id = 2
        msg = "テスト"
        speed = 1.5
        pitch = 0.3
        intonation = 1.2
        volume = 0.8
        
        # requestsのモック設定
        mock_query_response = Mock()
        mock_query_response.json.return_value = {
            "speedScale": 1.0,
            "pitchScale": 0.0,
            "intonationScale": 1.0,
            "volumeScale": 1.0
        }
        mock_query_response.raise_for_status = Mock()
        
        mock_synthesis_response = Mock()
        mock_synthesis_response.content = b"dummy_audio_data"
        mock_synthesis_response.raise_for_status = Mock()
        
        mock_requests_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        # soundfileのモック設定
        dummy_audio = np.array([[0.1, 0.2]], dtype=np.float32)
        mock_sf_read.return_value = (dummy_audio, 24000)
        
        # sounddeviceのモック設定
        mock_stream = MagicMock()
        mock_output_stream.return_value.__enter__.return_value = mock_stream
        
        # Act
        speak(style_id, msg, speedScale=speed, pitchScale=pitch, 
              intonationScale=intonation, volumeScale=volume)
        
        # Assert
        # synthesis APIに渡されたクエリデータの確認
        second_call = mock_requests_post.call_args_list[1]
        query_data = second_call[1]["json"]
        assert query_data["speedScale"] == speed
        assert query_data["pitchScale"] == pitch
        assert query_data["intonationScale"] == intonation
        assert query_data["volumeScale"] == volume

    @patch('pvv_mcp_server.mod_speak.pvv_mcp_server.mod_avatar_manager.set_anime_key')
    @patch('pvv_mcp_server.mod_speak.requests.post')
    def test_speak_audio_query_error(self, mock_requests_post, mock_set_anime_key):
        """異常系: audio_query APIエラー"""
        # Arrange
        style_id = 1
        msg = "エラーテスト"
        
        # requestsでエラーを発生させる
        mock_requests_post.side_effect = Exception("API connection failed")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            speak(style_id, msg)
        
        assert "VOICEVOX API通信エラー" in str(exc_info.value)
        
        # アニメーションキーは設定されない
        mock_set_anime_key.assert_not_called()

    @patch('pvv_mcp_server.mod_speak.pvv_mcp_server.mod_avatar_manager.set_anime_key')
    @patch('pvv_mcp_server.mod_speak.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak.sf.read')
    @patch('pvv_mcp_server.mod_speak.requests.post')
    def test_speak_synthesis_error(self, mock_requests_post, mock_sf_read, mock_output_stream, mock_set_anime_key):
        """異常系: synthesis APIエラー"""
        # Arrange
        style_id = 1
        msg = "合成エラーテスト"
        
        # audio_queryは成功
        mock_query_response = Mock()
        mock_query_response.json.return_value = {}
        mock_query_response.raise_for_status = Mock()
        
        # synthesisでエラー
        mock_synthesis_response = Mock()
        mock_synthesis_response.raise_for_status.side_effect = Exception("Synthesis failed")
        
        mock_requests_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            speak(style_id, msg)
        
        assert "VOICEVOX API通信エラー" in str(exc_info.value)

    @patch('pvv_mcp_server.mod_speak.pvv_mcp_server.mod_avatar_manager.set_anime_key')
    @patch('pvv_mcp_server.mod_speak.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak.sf.read')
    @patch('pvv_mcp_server.mod_speak.requests.post')
    def test_speak_audio_playback_error(self, mock_requests_post, mock_sf_read, mock_output_stream, mock_set_anime_key):
        """異常系: 音声再生エラー"""
        # Arrange
        style_id = 1
        msg = "再生エラーテスト"
        
        # requestsのモック設定(成功)
        mock_query_response = Mock()
        mock_query_response.json.return_value = {}
        mock_query_response.raise_for_status = Mock()
        
        mock_synthesis_response = Mock()
        mock_synthesis_response.content = b"dummy_audio_data"
        mock_synthesis_response.raise_for_status = Mock()
        
        mock_requests_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        # soundfileで音声読み込みエラー
        mock_sf_read.side_effect = Exception("Audio read failed")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            speak(style_id, msg)
        
        assert "音声再生エラー" in str(exc_info.value)
        
        # 口パクは設定されるが、finallyで立ち絵に戻される
        assert mock_set_anime_key.call_count == 2
        mock_set_anime_key.assert_any_call(style_id, "口パク")
        mock_set_anime_key.assert_any_call(style_id, "立ち絵")

    @patch('pvv_mcp_server.mod_speak.pvv_mcp_server.mod_avatar_manager.set_anime_key')
    @patch('pvv_mcp_server.mod_speak.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak.sf.read')
    @patch('pvv_mcp_server.mod_speak.requests.post')
    def test_speak_stream_write_error(self, mock_requests_post, mock_sf_read, mock_output_stream, mock_set_anime_key):
        """異常系: ストリーム書き込みエラー"""
        # Arrange
        style_id = 1
        msg = "書き込みエラーテスト"
        
        # requestsのモック設定(成功)
        mock_query_response = Mock()
        mock_query_response.json.return_value = {}
        mock_query_response.raise_for_status = Mock()
        
        mock_synthesis_response = Mock()
        mock_synthesis_response.content = b"dummy_audio_data"
        mock_synthesis_response.raise_for_status = Mock()
        
        mock_requests_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        # soundfileのモック設定(成功)
        dummy_audio = np.array([[0.1, 0.2]], dtype=np.float32)
        mock_sf_read.return_value = (dummy_audio, 24000)
        
        # stream.writeでエラー
        mock_stream = MagicMock()
        mock_stream.write.side_effect = Exception("Stream write failed")
        mock_output_stream.return_value.__enter__.return_value = mock_stream
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            speak(style_id, msg)
        
        assert "音声再生エラー" in str(exc_info.value)
        
        # finallyで立ち絵に戻される
        mock_set_anime_key.assert_any_call(style_id, "立ち絵")

    @patch('pvv_mcp_server.mod_speak.pvv_mcp_server.mod_avatar_manager.set_anime_key')
    @patch('pvv_mcp_server.mod_speak.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak.sf.read')
    @patch('pvv_mcp_server.mod_speak.requests.post')
    def test_speak_empty_message(self, mock_requests_post, mock_sf_read, mock_output_stream, mock_set_anime_key):
        """正常系: 空のメッセージでの呼び出し"""
        # Arrange
        style_id = 1
        msg = ""
        
        # requestsのモック設定
        mock_query_response = Mock()
        mock_query_response.json.return_value = {}
        mock_query_response.raise_for_status = Mock()
        
        mock_synthesis_response = Mock()
        mock_synthesis_response.content = b"dummy_audio_data"
        mock_synthesis_response.raise_for_status = Mock()
        
        mock_requests_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        # soundfileのモック設定
        dummy_audio = np.array([[0.0]], dtype=np.float32)
        mock_sf_read.return_value = (dummy_audio, 24000)
        
        # sounddeviceのモック設定
        mock_stream = MagicMock()
        mock_output_stream.return_value.__enter__.return_value = mock_stream
        
        # Act
        speak(style_id, msg)
        
        # Assert
        # 空のメッセージでも処理が正常に完了することを確認
        first_call = mock_requests_post.call_args_list[0]
        assert first_call[1]["params"]["text"] == ""
