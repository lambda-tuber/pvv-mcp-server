"""
test_speakers.py
mod_speakers.speakers関数のユニットテスト
"""
import pytest
import requests
import json
from unittest.mock import patch, MagicMock
from pvv_mcp_server import mod_speakers


class TestSpeakers:
    """speakers関数のテストクラス"""
    
    @pytest.fixture(autouse=True)
    def reset_cache(self):
        """各テストの前後でキャッシュをリセット"""
        mod_speakers._speakers_cache = None
        yield
        mod_speakers._speakers_cache = None
    
    def test_speakers_success(self):
        """正常系: API呼び出しが成功し、話者一覧を取得できる"""
        mock_data = [
            {
                "name": "四国めたん",
                "speaker_uuid": "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff",
                "styles": [
                    {"name": "ノーマル", "id": 2},
                    {"name": "あまあま", "id": 0}
                ]
            },
            {
                "name": "ずんだもん",
                "speaker_uuid": "388f246b-8c41-4ac1-8e2d-5d79f3ff56d9",
                "styles": [{"name": "ノーマル", "id": 3}]
            }
        ]
        
        with patch('pvv_mcp_server.mod_speakers.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.content = json.dumps(mock_data).encode("utf-8")  # bytesを返す
            mock_get.return_value = mock_response
            
            result = mod_speakers.speakers()
            
            # JSONに戻して比較
            decoded = json.loads(result.decode("utf-8"))
            assert decoded == mock_data
            mock_get.assert_called_once_with("http://localhost:50021/speakers")
            mock_response.raise_for_status.assert_called_once()
    
    def test_speakers_cache(self):
        """キャッシュ機能: 2回目の呼び出しではAPIを呼ばずキャッシュを返す"""
        mock_data = [{"name": "四国めたん"}]
        encoded_data = json.dumps(mock_data).encode("utf-8")
        
        with patch('pvv_mcp_server.mod_speakers.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.content = encoded_data
            mock_get.return_value = mock_response
            
            result1 = mod_speakers.speakers()
            result2 = mod_speakers.speakers()
            
            assert result1 is result2  # 同じキャッシュオブジェクト
            mock_get.assert_called_once()
    
    def test_speakers_api_error(self):
        """異常系: API呼び出しに失敗した場合"""
        with patch('pvv_mcp_server.mod_speakers.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("API Error")
            with pytest.raises(requests.exceptions.RequestException):
                mod_speakers.speakers()
    
    def test_speakers_http_error(self):
        """異常系: HTTPエラーが発生した場合"""
        with patch('pvv_mcp_server.mod_speakers.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
            mock_get.return_value = mock_response
            with pytest.raises(requests.exceptions.HTTPError):
                mod_speakers.speakers()
    
    def test_speakers_return_type(self):
        """戻り値の型検証: bytesが返ることを確認"""
        with patch('pvv_mcp_server.mod_speakers.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.content = b"[]"  # bytesで返す
            mock_get.return_value = mock_response
            
            result = mod_speakers.speakers()
            assert isinstance(result, (bytes, bytearray))
