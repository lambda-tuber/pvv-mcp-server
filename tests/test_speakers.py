"""
test_speakers.py
mod_speakers.pyのユニットテスト
"""
import pytest
from unittest.mock import patch, Mock
from pvv_mcp_server.mod_speakers import speakers


class TestSpeakers:
    """speakers関数のテストクラス"""
    
    @patch('pvv_mcp_server.mod_speakers.requests.get')
    def test_speakers_success(self, mock_get):
        """正常系: 話者一覧が正しく取得できること"""
        # モックレスポンスの準備
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "name": "四国めたん",
                "speaker_uuid": "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff",
                "styles": [
                    {"name": "ノーマル", "id": 2},
                    {"name": "あまあま", "id": 0},
                    {"name": "ツンツン", "id": 6}
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
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # テスト実行
        result = speakers()
        
        # 検証
        mock_get.assert_called_once_with("http://localhost:50021/speakers")
        assert len(result) == 2
        assert result[0]["name"] == "四国めたん"
        assert result[1]["name"] == "ずんだもん"
        assert len(result[0]["styles"]) == 3
    
    @patch('pvv_mcp_server.mod_speakers.requests.get')
    def test_speakers_empty_list(self, mock_get):
        """正常系: 話者が0件の場合"""
        # モックレスポンスの準備
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # テスト実行
        result = speakers()
        
        # 検証
        assert result == []
    
    @patch('pvv_mcp_server.mod_speakers.requests.get')
    def test_speakers_api_error(self, mock_get):
        """異常系: API呼び出しに失敗した場合"""
        # モックで例外を発生させる
        mock_get.side_effect = Exception("API Error")
        
        # テスト実行と検証
        with pytest.raises(Exception) as excinfo:
            speakers()
        assert "API Error" in str(excinfo.value)

        