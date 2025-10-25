"""
test_speaker_info.py
mod_speaker_info.pyの単体テスト
"""
import pytest
import requests
import json
from unittest.mock import patch, MagicMock
from pvv_mcp_server.mod_speaker_info import speaker_info


class TestSpeakerInfo:
    """speaker_info関数のテストクラス"""
    
    @patch("pvv_mcp_server.mod_speaker_info.requests.get")
    def test_speaker_info_with_uuid(self, mock_get):
        """UUIDを指定した場合のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "policy": "test_policy",
            "portrait": "test_portrait_url",
            "style_infos": []
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # テスト実行
        test_uuid = "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff"
        result = speaker_info(test_uuid)
        
        # 検証
        assert result == {
            "policy": "test_policy",
            "portrait": "test_portrait_url",
            "style_infos": []
        }
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "http://localhost:50021/speaker_info"
        assert call_args[1]["params"]["speaker_uuid"] == test_uuid
    
    @patch("pvv_mcp_server.mod_speaker_info.speakers")
    @patch("pvv_mcp_server.mod_speaker_info.requests.get")
    def test_speaker_info_with_name(self, mock_get, mock_speakers):
        """話者名を指定した場合のテスト"""
        # speakersのモック設定
        mock_speakers_data = [
            {
                "name": "四国めたん",
                "speaker_uuid": "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff",
                "styles": []
            },
            {
                "name": "ずんだもん",
                "speaker_uuid": "388f246b-8c41-4ac1-8e2d-5d79f3ff56d9",
                "styles": []
            }
        ]
        # json.dumps()を使って正しいJSON文字列に変換
        mock_speakers.return_value = json.dumps(mock_speakers_data).encode("utf-8")
        
        # requestsのモック設定
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "policy": "test_policy",
            "portrait": "test_portrait_url",
            "style_infos": []
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # テスト実行
        result = speaker_info("四国")
        
        # 検証
        assert result == {
            "policy": "test_policy",
            "portrait": "test_portrait_url",
            "style_infos": []
        }
        mock_speakers.assert_called_once()
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["params"]["speaker_uuid"] == "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff"
    
    @patch("pvv_mcp_server.mod_speaker_info.speakers")
    def test_speaker_info_with_invalid_name(self, mock_speakers):
        """存在しない話者名を指定した場合のテスト"""
        # speakersのモック設定
        mock_speakers_data = [
            {
                "name": "四国めたん",
                "speaker_uuid": "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff",
                "styles": []
            }
        ]
        # json.dumps()を使って正しいJSON文字列に変換
        mock_speakers.return_value = json.dumps(mock_speakers_data).encode("utf-8")
        
        # テスト実行と検証
        with pytest.raises(ValueError, match="話者 '存在しない話者' が見つかりませんでした"):
            speaker_info("存在しない話者")
    
    @patch("pvv_mcp_server.mod_speaker_info.requests.get")
    def test_speaker_info_api_error(self, mock_get):
        """APIリクエストが失敗した場合のテスト"""
        # モックの設定（エラーを発生させる）
        mock_get.side_effect = requests.RequestException("Connection error")
        
        # テスト実行と検証
        test_uuid = "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff"
        with pytest.raises(requests.RequestException, match="speaker_info APIリクエストが失敗しました"):
            speaker_info(test_uuid)
    
    @patch("pvv_mcp_server.mod_speaker_info.speakers")
    @patch("pvv_mcp_server.mod_speaker_info.requests.get")
    def test_speaker_info_with_partial_match(self, mock_get, mock_speakers):
        """部分一致で話者を検索するテスト"""
        # speakersのモック設定
        mock_speakers_data = [
            {
                "name": "四国めたん",
                "speaker_uuid": "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff",
                "styles": []
            },
            {
                "name": "ずんだもん",
                "speaker_uuid": "388f246b-8c41-4ac1-8e2d-5d79f3ff56d9",
                "styles": []
            }
        ]
        # json.dumps()を使って正しいJSON文字列に変換
        mock_speakers.return_value = json.dumps(mock_speakers_data).encode("utf-8")
        
        # requestsのモック設定
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "policy": "test_policy",
            "portrait": "test_portrait_url",
            "style_infos": []
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # テスト実行（"めたん"で部分一致）
        result = speaker_info("めたん")
        
        # 検証
        assert result["policy"] == "test_policy"
        call_args = mock_get.call_args
        assert call_args[1]["params"]["speaker_uuid"] == "7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff"