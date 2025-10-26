"""
test_service.py
mod_service.pyの単体テスト
"""
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
import pvv_mcp_server.mod_service


class TestService:
    """mod_serviceの各ツール・リソース関数のテストクラス"""
    
    # ========================================
    # speak関数のテスト
    # ========================================
    @pytest.mark.asyncio
    @patch("pvv_mcp_server.mod_service.mod_speak.speak")
    async def test_speak_success(self, mock_speak):
        """speak関数の正常系テスト"""
        # モックの設定
        mock_speak.return_value = None
        
        # テスト実行
        result = await pvv_mcp_server.mod_service.speak(
            style_id=6,
            msg="テストメッセージ",
            speedScale=1.0,
            pitchScale=0.0,
            intonationScale=1.0,
            volumeScale=1.0
        )
        
        # 検証
        assert result == "音声合成・再生が完了しました。(style_id=6)"
        mock_speak.assert_called_once_with(
            style_id=6,
            msg="テストメッセージ",
            speedScale=1.0,
            pitchScale=0.0,
            intonationScale=1.0,
            volumeScale=1.0
        )
    
    @pytest.mark.asyncio
    @patch("pvv_mcp_server.mod_service.mod_speak.speak")
    async def test_speak_error(self, mock_speak):
        """speak関数のエラー系テスト"""
        # モックの設定（エラーを発生させる）
        mock_speak.side_effect = Exception("音声合成エラー")
        
        # テスト実行
        result = await pvv_mcp_server.mod_service.speak(
            style_id=6,
            msg="テストメッセージ"
        )
        
        # 検証
        assert "エラーが発生しました" in result
        assert "音声合成エラー" in result
    
    # ========================================
    # speak_metan_aska関数のテスト
    # ========================================
    @pytest.mark.asyncio
    @patch("pvv_mcp_server.mod_service.speak")
    async def test_speak_metan_aska(self, mock_speak):
        """speak_metan_aska関数のテスト"""
        # モックの設定
        mock_speak.return_value = "音声合成・再生が完了しました。(style_id=6)"
        
        # テスト実行
        result = await pvv_mcp_server.mod_service.speak_metan_aska("アスカのテストメッセージ")
        
        # 検証
        assert result == "音声合成・再生が完了しました。(style_id=6)"
    
    # ========================================
    # speak_kurono_neko関数のテスト
    # ========================================
    @pytest.mark.asyncio
    @patch("pvv_mcp_server.mod_service.speak")
    async def test_speak_kurono_neko(self, mock_speak):
        """speak_kurono_neko関数のテスト"""
        # モックの設定
        mock_speak.return_value = "音声合成・再生が完了しました。(style_id=11)"
        
        # テスト実行
        result = await pvv_mcp_server.mod_service.speak_kurono_neko("ネコのテストメッセージ")
        
        # 検証
        assert result == "音声合成・再生が完了しました。(style_id=11)"
    
    # ========================================
    # emotion関数のテスト
    # ========================================
    @pytest.mark.asyncio
    @patch("pvv_mcp_server.mod_service._avatar_enbled", True)
    @patch("pvv_mcp_server.mod_service.mod_emotion.emotion")
    async def test_emotion_success(self, mock_emotion):
        """emotion関数の正常系テスト"""
        # モックの設定
        mock_emotion.return_value = None
        
        # テスト実行
        result = await pvv_mcp_server.mod_service.emotion(style_id=6, emo="えがお")
        
        # 検証
        assert result == "感情表現完了: えがお"
        mock_emotion.assert_called_once_with(6, "えがお")
    
    @pytest.mark.asyncio
    @patch("pvv_mcp_server.mod_service._avatar_enbled", True)
    async def test_emotion_invalid_emotion(self):
        """emotion関数の不正な感情指定テスト"""
        # テスト実行
        result = await pvv_mcp_server.mod_service.emotion(style_id=6, emo="不正な感情")
        
        # 検証
        print("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")
        print(result)
        assert "エラー: emo は" in result
    
    @pytest.mark.asyncio
    @patch("pvv_mcp_server.mod_service._avatar_enbled", False)
    async def test_emotion_disabled(self):
        """アバター無効時のemotion関数テスト"""
        # テスト実行
        result = await pvv_mcp_server.mod_service.emotion(style_id=6, emo="えがお")
        
        # 検証
        assert result == "avatar disabled."
    
    # ========================================
    # リソース関数のテスト
    # ========================================
    @patch("pvv_mcp_server.mod_service.mod_speakers.speakers")
    def test_resource_speakers_success(self, mock_speakers):
        """resource_speakers関数の正常系テスト"""
        # モックの設定
        mock_data = [{"name": "四国めたん", "speaker_uuid": "test-uuid"}]
        mock_speakers.return_value = json.dumps(mock_data).encode("utf-8")
        
        # テスト実行
        result =pvv_mcp_server.mod_service.resource_speakers()
        
        # 検証
        assert result == json.dumps(mock_data).encode("utf-8")
        mock_speakers.assert_called_once()
    
    @patch("pvv_mcp_server.mod_service.mod_speakers.speakers")
    def test_resource_speakers_error(self, mock_speakers):
        """resource_speakers関数のエラー系テスト"""
        # モックの設定（エラーを発生させる）
        mock_speakers.side_effect = Exception("API接続エラー")
        
        # テスト実行
        result =pvv_mcp_server.mod_service.resource_speakers()
        
        # 検証
        assert "エラー" in result
        assert "API接続エラー" in result
    
    @patch("pvv_mcp_server.mod_service.mod_speaker_info.speaker_info")
    def test_resource_speaker_info_success(self, mock_speaker_info):
        """resource_speaker_info関数の正常系テスト"""
        # モックの設定
        mock_data = {
            "policy": "test_policy",
            "portrait": "test_url"
        }
        mock_speaker_info.return_value = mock_data
        
        # テスト実行
        result =pvv_mcp_server.mod_service.resource_speaker_info("四国めたん")
        
        # 検証
        result_dict = json.loads(result)
        assert result_dict == mock_data
        mock_speaker_info.assert_called_once_with("四国めたん")
    
    @patch("pvv_mcp_server.mod_service.mod_speaker_info.speaker_info")
    def test_resource_speaker_info_error(self, mock_speaker_info):
        """resource_speaker_info関数のエラー系テスト"""
        # モックの設定（エラーを発生させる）
        mock_speaker_info.side_effect = ValueError("話者が見つかりません")
        
        # テスト実行
        result =pvv_mcp_server.mod_service.resource_speaker_info("存在しない話者")
        
        # 検証
        assert "エラー" in result
        assert "話者が見つかりません" in result
    
    # ========================================
    # プロンプト関数のテスト
    # ========================================
    def test_resource_ai_aska(self):
        """resource_ai_aska関数のテスト"""
        # テスト実行
        result =pvv_mcp_server.mod_service.resource_ai_aska()
        
        # 検証
        assert "アスカ" in result
        assert "AIペルソナ" in result
        assert "音声会話仕様" in result
    
    def test_prompt_ai_aska(self):
        """prompt_ai_aska関数のテスト"""
        # テスト実行
        result =pvv_mcp_server.mod_service.prompt_ai_aska()
        
        # 検証
        assert result ==pvv_mcp_server.mod_service.PROMPT_ASKA_TEXT
        assert "アスカ" in result
    
    def test_resource_ai_touhou(self):
        """resource_ai_touhou関数のテスト"""
        # テスト実行
        result =pvv_mcp_server.mod_service.resource_ai_touhou()
        
        # 検証
        assert "霊夢" in result or "魔理沙" in result
        assert "AIペルソナ" in result
    
    def test_prompt_ai_touhou(self):
        """prompt_ai_touhou関数のテスト"""
        # テスト実行
        result =pvv_mcp_server.mod_service.prompt_ai_touhou()
        
        # 検証
        assert result ==pvv_mcp_server.mod_service.PROMPT_TOUHOU_TEXT
        assert "霊夢" in result or "魔理沙" in result
    
    # ========================================
    # start関数のテスト
    # ========================================
    @patch("pvv_mcp_server.mod_service.start_mcp")
    def test_start_without_avatar(self, mock_start_mcp):
        """アバター無効時のstart関数テスト"""
        # テスト実行
        test_conf = {"avatar": {"enabled": False}}
        pvv_mcp_server.mod_service.start(test_conf)
        
        # 検証
        mock_start_mcp.assert_called_once_with(test_conf)
        assert pvv_mcp_server.mod_service._avatar_enbled is False
    
    @patch("pvv_mcp_server.mod_service.start_mcp_avatar")
    def test_start_with_avatar(self, mock_start_mcp_avatar):
        """アバター有効時のstart関数テスト"""
        # テスト実行
        test_conf = {"avatar": {"enabled": True}}
        pvv_mcp_server.mod_service.start(test_conf)
        
        # 検証
        mock_start_mcp_avatar.assert_called_once()
        assert pvv_mcp_server.mod_service._avatar_enbled is True