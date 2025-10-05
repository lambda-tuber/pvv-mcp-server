"""
test_speak.py
mod_speak.pyのユニットテスト
"""

import io
import pytest
import numpy as np
import soundfile as sf
from unittest.mock import patch, MagicMock
from pvv_mcp_server.mod_speak import speak


def make_wav_bytes(data: np.ndarray, samplerate=24000):
    """NumPy配列から正規のWAVバイト列を生成"""
    buf = io.BytesIO()
    sf.write(buf, data, samplerate, format="WAV")
    return buf.getvalue()


class TestSpeak:
    """speak関数のテストクラス"""
    
    @patch('pvv_mcp_server.mod_speak.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak.requests')
    def test_speak_success_default_params(self, mock_requests, mock_stream):
        """正常系: デフォルトパラメータで音声合成・再生が成功する"""
        # モックの設定
        mock_query_response = MagicMock()
        mock_query_response.json.return_value = {
            "speedScale": 1.0,
            "pitchScale": 0.0,
            "intonationScale": 1.0,
            "volumeScale": 1.0
        }

        # WAVデータ生成（モノラル）
        pcm = np.array([[0.1], [0.2], [-0.1]], dtype=np.float32)
        wav_bytes = make_wav_bytes(pcm, samplerate=24000)
        mock_synthesis_response = MagicMock()
        mock_synthesis_response.content = wav_bytes
        
        mock_requests.post.side_effect = [mock_query_response, mock_synthesis_response]

        # sd.OutputStream のモック
        mock_stream_instance = MagicMock()
        mock_stream.return_value.__enter__.return_value = mock_stream_instance
        
        # 実行
        speak(style_id=6, msg="こんにちは")
        
        # 検証
        assert mock_requests.post.call_count == 2
        first_call = mock_requests.post.call_args_list[0]
        assert "audio_query" in first_call[0][0]
        assert first_call[1]["params"]["text"] == "こんにちは"
        assert first_call[1]["params"]["speaker"] == 6
        
        second_call = mock_requests.post.call_args_list[1]
        assert "synthesis" in second_call[0][0]
        assert second_call[1]["params"]["speaker"] == 6
        
        mock_stream_instance.write.assert_called_once()
    
    @patch('pvv_mcp_server.mod_speak.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak.requests')
    def test_speak_success_custom_params(self, mock_requests, mock_stream):
        """正常系: カスタムパラメータで音声合成・再生が成功する"""
        mock_query_response = MagicMock()
        mock_query_response.json.return_value = {
            "speedScale": 1.0,
            "pitchScale": 0.0,
            "intonationScale": 1.0,
            "volumeScale": 1.0
        }

        pcm = np.array([[0.1], [0.2]], dtype=np.float32)
        wav_bytes = make_wav_bytes(pcm, samplerate=24000)
        mock_synthesis_response = MagicMock()
        mock_synthesis_response.content = wav_bytes
        
        mock_requests.post.side_effect = [mock_query_response, mock_synthesis_response]
        mock_stream.return_value.__enter__.return_value = MagicMock()
        
        speak(
            style_id=10,
            msg="テストメッセージ",
            speedScale=1.5,
            pitchScale=0.3,
            intonationScale=1.2,
            volumeScale=0.8
        )
        
        second_call = mock_requests.post.call_args_list[1]
        query_data = second_call[1]["json"]
        assert query_data["speedScale"] == 1.5
        assert query_data["pitchScale"] == 0.3
        assert query_data["intonationScale"] == 1.2
        assert query_data["volumeScale"] == 0.8
    
    @patch('pvv_mcp_server.mod_speak.requests.post')
    def test_speak_audio_query_error(self, mock_post):
        """異常系: audio_queryでエラーが発生する"""
        mock_post.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            speak(style_id=6, msg="エラーテスト")
        
        assert "VOICEVOX API通信エラー" in str(exc_info.value)
    
    @patch('pvv_mcp_server.mod_speak.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak.requests.post')
    def test_speak_synthesis_error(self, mock_post, mock_stream):
        """異常系: synthesisでエラーが発生する"""
        mock_query_response = MagicMock()
        mock_query_response.json.return_value = {"speedScale": 1.0}
        
        mock_post.side_effect = [
            mock_query_response,
            Exception("Synthesis Error")
        ]
        
        with pytest.raises(Exception) as exc_info:
            speak(style_id=6, msg="エラーテスト")
        
        assert "VOICEVOX API通信エラー" in str(exc_info.value)
    
    @patch('pvv_mcp_server.mod_speak.sd.OutputStream')
    @patch('pvv_mcp_server.mod_speak.requests.post')
    def test_speak_playback_error(self, mock_post, mock_stream):
        """異常系: 音声再生でエラーが発生する"""
        mock_query_response = MagicMock()
        mock_query_response.json.return_value = {"speedScale": 1.0}
        
        pcm = np.array([[0.1]], dtype=np.float32)
        wav_bytes = make_wav_bytes(pcm, samplerate=24000)
        mock_synthesis_response = MagicMock()
        mock_synthesis_response.content = wav_bytes
        
        mock_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        mock_stream_instance = MagicMock()
        mock_stream_instance.write.side_effect = Exception("Playback Error")
        mock_stream.return_value.__enter__.return_value = mock_stream_instance
        
        with pytest.raises(Exception) as exc_info:
            speak(style_id=6, msg="再生エラーテスト")
        
        assert "音声再生エラー" in str(exc_info.value)
