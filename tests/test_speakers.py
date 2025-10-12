"""
test_speakers.py
mod_speakers.speakers関数のユニットテスト
"""
import pytest
import requests
from unittest.mock import patch, MagicMock
from pvv_mcp_server.mod_speakers import speakers, _cache


class TestSpeakers:
    """speakers関数のテストクラス"""
    
    @pytest.fixture(autouse=True)
    def reset_cache(self):
        """各テストの前後でキャッシュをリセット"""
        import pvv_mcp_server.mod_speakers as mod
        mod._cache = None
        yield
        mod._cache = None
    
    def test_speakers_success(self):
        """正常系: API呼び出しが成功し、話者一覧を取得できる"""
        # モックレスポンスデータ
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
                "styles": [
                    {"name": "ノーマル", "id": 3}
                ]
            }
        ]
        
        # requests.getをモック
        with patch('pvv_mcp_server.mod_speakers.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_data
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            # 関数実行
            result = speakers()
            
            # 検証
            assert result == mock_data
            mock_get.assert_called_once_with("http://localhost:50021/speakers")
            mock_response.raise_for_status.assert_called_once()
    
    def test_speakers_cache(self):
        """キャッシュ機能: 2回目の呼び出しではAPIを呼ばずキャッシュを返す"""
        mock_data = [
            {
                "name": "四国めたん",
                "speaker_uuid": "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff",
                "styles": [{"name": "ノーマル", "id": 2}]
            }
        ]
        
        with patch('pvv_mcp_server.mod_speakers.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_data
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            # 1回目の呼び出し
            result1 = speakers()
            assert result1 == mock_data
            assert mock_get.call_count == 1
            
            # 2回目の呼び出し（キャッシュから返される）
            result2 = speakers()
            assert result2 == mock_data
            assert mock_get.call_count == 1  # API呼び出しは1回のまま
            
            # 結果が同じオブジェクトであることを確認
            assert result1 is result2
    
    def test_speakers_api_error(self):
        """異常系: APIエラーが発生した場合、例外が発生する"""
        with patch('pvv_mcp_server.mod_speakers.requests.get') as mock_get:
            # HTTPエラーをシミュレート
            mock_get.side_effect = requests.exceptions.RequestException("API Error")
            
            # 例外が発生することを確認
            with pytest.raises(requests.exceptions.RequestException):
                speakers()
    
    def test_speakers_http_error(self):
        """異常系: HTTPステータスエラーが発生した場合、例外が発生する"""
        with patch('pvv_mcp_server.mod_speakers.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
            mock_get.return_value = mock_response
            
            # 例外が発生することを確認
            with pytest.raises(requests.exceptions.HTTPError):
                speakers()
    
    def test_speakers_return_type(self):
        """戻り値の型検証: Listが返されることを確認"""
        mock_data = []
        
        with patch('pvv_mcp_server.mod_speakers.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_data
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            result = speakers()
            
            assert isinstance(result, list)