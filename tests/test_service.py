"""
test_service.py
mod_service モジュールのユニットテスト
"""
import pytest
from unittest.mock import patch, MagicMock
from pvv_mcp_server import mod_service


class TestService:
    """mod_service モジュールのテストクラス"""

    # ========== speak ==========
    @pytest.mark.asyncio
    async def test_speak_success(self):
        """speak 関数が正常に動作することを確認"""
        with patch('pvv_mcp_server.mod_service.mod_speak.speak') as mock_speak:
            mock_speak.return_value = None

            result = await mod_service.speak(
                style_id=1, msg="テスト", speedScale=1.1, pitchScale=0.2, intonationScale=1.3, volumeScale=0.9
            )

            mock_speak.assert_called_once_with(
                style_id=1, msg="テスト",
                speedScale=1.1, pitchScale=0.2,
                intonationScale=1.3, volumeScale=0.9
            )
            assert result == "音声合成・再生が完了しました。(style_id=1, msg='テスト')"

    @pytest.mark.asyncio
    async def test_speak_error(self):
        """speak 関数がエラー時に適切に処理されることを確認"""
        with patch('pvv_mcp_server.mod_service.mod_speak.speak') as mock_speak:
            mock_speak.side_effect = Exception("テストエラー")

            result = await mod_service.speak(style_id=1, msg="エラーテスト")

            assert result == "エラーが発生しました: テストエラー"

    # ========== speak_metan_aska ==========
    @pytest.mark.asyncio
    async def test_speak_metan_aska_success(self):
        """speak_metan_aska 関数が正常に動作することを確認"""
        with patch('pvv_mcp_server.mod_service.mod_speak_metan_aska.speak_metan_aska') as mock_speak:
            mock_speak.return_value = None

            result = await mod_service.speak_metan_aska("テストメッセージ")

            mock_speak.assert_called_once_with("テストメッセージ")
            assert result == "発話完了: テストメッセージ"

    @pytest.mark.asyncio
    async def test_speak_metan_aska_error(self):
        """speak_metan_aska 関数がエラー時に適切に処理されることを確認"""
        with patch('pvv_mcp_server.mod_service.mod_speak_metan_aska.speak_metan_aska') as mock_speak:
            mock_speak.side_effect = Exception("テストエラー")

            result = await mod_service.speak_metan_aska("エラーテスト")

            assert result == "エラー: テストエラー"

    # ========== speakers ==========
    def test_speakers_success(self):
        """speakers リソースが正常に JSON を返すことを確認"""
        fake_data = [{"id": 1, "name": "テスト話者"}]
        with patch('pvv_mcp_server.mod_service.mod_speakers.speakers', return_value=fake_data):
            result = mod_service.speakers()

            import json
            expected = json.dumps(fake_data, ensure_ascii=False, indent=2)
            assert result == expected

    def test_speakers_error(self):
        """speakers リソースがエラー時に 'エラー: ...' を返すことを確認"""
        with patch('pvv_mcp_server.mod_service.mod_speakers.speakers', side_effect=Exception("テストエラー")):
            result = mod_service.speakers()
            assert result == "エラー: テストエラー"

    # ========== start ==========
    def test_start(self):
        """start 関数が mcp.run() を呼び出すことを確認"""
        with patch.object(mod_service.mcp, 'run') as mock_run:
            mock_run.return_value = None
            mod_service.start()
            mock_run.assert_called_once_with(transport="stdio")

    def test_mcp_server_name(self):
        """MCP サーバの名前が正しく設定されていることを確認"""
        assert mod_service.mcp.name == "pvv-mcp-server"
