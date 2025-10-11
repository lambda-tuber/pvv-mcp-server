"""
test_speaker_info.py
mod_speaker_info.pyのユニットテスト
"""
import pytest
from unittest.mock import patch, MagicMock
import requests
from pvv_mcp_server.mod_speaker_info import speaker_info


class TestSpeakerInfo:
    """speaker_info関数のテストクラス"""
    
    @patch('pvv_mcp_server.mod_speaker_info.requests.get')
    def test_speaker_info_with_uuid(self, mock_get):
        """UUIDを指定した場合のテスト"""
        # モックのレスポンス設定
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "policy": "テストポリシー",
            "portrait": "test.png",
            "style_infos": []
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # テスト実行
        test_uuid = "test-uuid-1234-5678"
        result = speaker_info(test_uuid)
        
        # 検証
        assert result["policy"] == "テストポリシー"
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["params"]["speaker_uuid"] == test_uuid
    
    @patch('pvv_mcp_server.mod_speaker_info.speakers')
    @patch('pvv_mcp_server.mod_speaker_info.requests.get')
    def test_speaker_info_with_name(self, mock_get, mock_speakers):
        """話者名を指定した場合のテスト"""
        # speakers関数のモック
        mock_speakers.return_value = [
            {
                "name": "四国めたん",
                "speaker_uuid": "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff"
            },
            {
                "name": "ずんだもん",
                "speaker_uuid": "388f246b-8c41-4ac1-8e2d-5d79f3ff56d9"
            }
        ]
        
        # requests.getのモック
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "policy": "めたんポリシー",
            "portrait": "metan.png",
            "style_infos": []
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # テスト実行（部分一致）
        result = speaker_info("めたん")
        
        # 検証
        assert result["policy"] == "めたんポリシー"
        mock_speakers.assert_called_once()
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["params"]["speaker_uuid"] == "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff"
    
    @patch('pvv_mcp_server.mod_speaker_info.speakers')
    def test_speaker_info_name_not_found(self, mock_speakers):
        """存在しない話者名を指定した場合のテスト"""
        # speakers関数のモック
        mock_speakers.return_value = [
            {
                "name": "四国めたん",
                "speaker_uuid": "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff"
            }
        ]
        
        # テスト実行と検証
        with pytest.raises(ValueError, match="話者 '存在しない' が見つかりませんでした。"):
            speaker_info("存在しない")
    
    @patch('pvv_mcp_server.mod_speaker_info.requests.get')
    def test_speaker_info_api_error(self, mock_get):
        """APIリクエストが失敗した場合のテスト"""
        # requests.getが例外を発生させる
        mock_get.side_effect = requests.RequestException("接続エラー")
        
        # テスト実行と検証
        with pytest.raises(requests.RequestException, match="speaker_info APIリクエストが失敗しました"):
            speaker_info("test-uuid-1234")
    
    @patch('pvv_mcp_server.mod_speaker_info.speakers')
    @patch('pvv_mcp_server.mod_speaker_info.requests.get')
    def test_speaker_info_case_insensitive(self, mock_get, mock_speakers):
        """大文字小文字を無視した検索のテスト"""
        # speakers関数のモック
        mock_speakers.return_value = [
            {
                "name": "四国めたん",
                "speaker_uuid": "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff"
            }
        ]
        
        # requests.getのモック
        mock_response = MagicMock()
        mock_response.json.return_value = {"policy": "test"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # テスト実行（大文字で検索）
        result = speaker_info("めたん")
        
        # 検証
        assert result["policy"] == "test"
        call_args = mock_get.call_args
        assert call_args[1]["params"]["speaker_uuid"] == "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff"

