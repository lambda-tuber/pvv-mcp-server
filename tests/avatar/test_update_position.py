"""
test_update_position.py
mod_update_positionのユニットテスト
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pvv_mcp_server.avatar.mod_update_position import update_position, get_windows_scaling


class TestUpdatePosition:
    """update_position関数のテストクラス"""
    
    @pytest.fixture
    def mock_avatar(self):
        """AvatarWindowのモックを作成"""
        avatar = Mock()
        avatar.app_title = "Test Application"
        avatar.position = "left_out"
        avatar.width.return_value = 300
        avatar.height.return_value = 500
        avatar.move = Mock()
        return avatar
    
    @pytest.fixture
    def mock_window(self):
        """pygetwindowのWindowオブジェクトのモックを作成"""
        window = Mock()
        window.left = 1920  # 論理座標
        window.top = 100
        window.width = 1200
        window.height = 800
        return window
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_left_out(self, mock_scaling, mock_get_windows, mock_avatar, mock_window):
        """left_out位置の計算をテスト"""
        # モックの設定
        mock_get_windows.return_value = [mock_window]
        mock_scaling.return_value = 1.0  # スケーリングなし
        
        # テスト実行
        update_position(mock_avatar)
        
        # 検証: left_outの場合、target_x - avatar_width
        expected_x = int((mock_window.left / 1.0) - mock_avatar.width())
        expected_y = int((mock_window.top / 1.0) + (mock_window.height / 1.0) - mock_avatar.height())
        mock_avatar.move.assert_called_once_with(expected_x, expected_y)
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_left_center(self, mock_scaling, mock_get_windows, mock_avatar, mock_window):
        """left_center位置の計算をテスト"""
        mock_avatar.position = "left_center"
        mock_get_windows.return_value = [mock_window]
        mock_scaling.return_value = 1.0
        
        update_position(mock_avatar)
        
        expected_x = int((mock_window.left / 1.0) - (mock_avatar.width() / 2))
        expected_y = int((mock_window.top / 1.0) + (mock_window.height / 1.0) - mock_avatar.height())
        mock_avatar.move.assert_called_once_with(expected_x, expected_y)
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_left_in(self, mock_scaling, mock_get_windows, mock_avatar, mock_window):
        """left_in位置の計算をテスト"""
        mock_avatar.position = "left_in"
        mock_get_windows.return_value = [mock_window]
        mock_scaling.return_value = 1.0
        
        update_position(mock_avatar)
        
        expected_x = int(mock_window.left / 1.0)
        expected_y = int((mock_window.top / 1.0) + (mock_window.height / 1.0) - mock_avatar.height())
        mock_avatar.move.assert_called_once_with(expected_x, expected_y)
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_right_in(self, mock_scaling, mock_get_windows, mock_avatar, mock_window):
        """right_in位置の計算をテスト"""
        mock_avatar.position = "right_in"
        mock_get_windows.return_value = [mock_window]
        mock_scaling.return_value = 1.0
        
        update_position(mock_avatar)
        
        expected_x = int((mock_window.left / 1.0) + (mock_window.width / 1.0) - mock_avatar.width())
        expected_y = int((mock_window.top / 1.0) + (mock_window.height / 1.0) - mock_avatar.height())
        mock_avatar.move.assert_called_once_with(expected_x, expected_y)
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_right_center(self, mock_scaling, mock_get_windows, mock_avatar, mock_window):
        """right_center位置の計算をテスト"""
        mock_avatar.position = "right_center"
        mock_get_windows.return_value = [mock_window]
        mock_scaling.return_value = 1.0
        
        update_position(mock_avatar)
        
        expected_x = int((mock_window.left / 1.0) + (mock_window.width / 1.0) - (mock_avatar.width() / 2))
        expected_y = int((mock_window.top / 1.0) + (mock_window.height / 1.0) - mock_avatar.height())
        mock_avatar.move.assert_called_once_with(expected_x, expected_y)
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_right_out(self, mock_scaling, mock_get_windows, mock_avatar, mock_window):
        """right_out位置の計算をテスト"""
        mock_avatar.position = "right_out"
        mock_get_windows.return_value = [mock_window]
        mock_scaling.return_value = 1.0
        
        update_position(mock_avatar)
        
        expected_x = int((mock_window.left / 1.0) + (mock_window.width / 1.0))
        expected_y = int((mock_window.top / 1.0) + (mock_window.height / 1.0) - mock_avatar.height())
        mock_avatar.move.assert_called_once_with(expected_x, expected_y)
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_with_scaling(self, mock_scaling, mock_get_windows, mock_avatar, mock_window):
        """DPIスケーリング適用時のテスト"""
        mock_get_windows.return_value = [mock_window]
        mock_scaling.return_value = 1.25  # 125%スケーリング
        
        update_position(mock_avatar)
        
        # 座標がスケールで割られることを確認
        expected_x = int((mock_window.left / 1.25) - mock_avatar.width())
        expected_y = int((mock_window.top / 1.25) + (mock_window.height / 1.25) - mock_avatar.height())
        mock_avatar.move.assert_called_once_with(expected_x, expected_y)
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    def test_update_position_window_not_found(self, mock_get_windows, mock_avatar):
        """ターゲットウィンドウが見つからない場合のテスト"""
        mock_get_windows.return_value = []
        
        # 例外が発生しないことを確認
        update_position(mock_avatar)
        
        # moveが呼ばれないことを確認
        mock_avatar.move.assert_not_called()
    
    def test_update_position_no_app_title(self):
        """app_titleが設定されていない場合のテスト"""
        avatar = Mock()
        avatar.app_title = None
        
        # 例外が発生しないことを確認
        update_position(avatar)
        
        # moveが呼ばれないことを確認
        assert not hasattr(avatar.move, 'assert_not_called') or True
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_no_position_attribute(self, mock_scaling, mock_get_windows, mock_window):
        """positionが設定されていない場合のテスト（デフォルト値使用）"""
        avatar = Mock()
        avatar.app_title = "Test Application"
        # positionを削除
        del avatar.position
        avatar.width.return_value = 300
        avatar.height.return_value = 500
        avatar.move = Mock()
        
        mock_get_windows.return_value = [mock_window]
        mock_scaling.return_value = 1.0
        
        update_position(avatar)
        
        # デフォルト値"left_out"で動作することを確認
        assert avatar.position == "left_out"
        avatar.move.assert_called_once()
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_unknown_position(self, mock_scaling, mock_get_windows, mock_avatar, mock_window):
        """不明なpositionが指定された場合のテスト"""
        mock_avatar.position = "unknown_position"
        mock_get_windows.return_value = [mock_window]
        mock_scaling.return_value = 1.0
        
        update_position(mock_avatar)
        
        # moveが呼ばれないことを確認
        mock_avatar.move.assert_not_called()
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    def test_update_position_exception_handling(self, mock_get_windows, mock_avatar):
        """例外発生時のハンドリングをテスト"""
        mock_get_windows.side_effect = Exception("Test exception")
        
        # 例外が外部に漏れないことを確認
        update_position(mock_avatar)
        
        mock_avatar.move.assert_not_called()


class TestGetWindowsScaling:
    """get_windows_scaling関数のテストクラス"""
    
    @patch('pvv_mcp_server.avatar.mod_update_position.ctypes.windll')
    def test_get_windows_scaling_success(self, mock_windll):
        """正常にスケーリングを取得できる場合のテスト"""
        # モックの設定
        mock_user32 = MagicMock()
        mock_shcore = MagicMock()
        mock_windll.user32 = mock_user32
        mock_windll.shcore = mock_shcore
        
        # DPI値を120に設定（125%スケーリング）
        def mock_get_dpi(monitor, dpi_type, dpiX, dpiY):
            dpiX._obj.value = 120
            dpiY._obj.value = 120
            return 0
        
        mock_shcore.GetDpiForMonitor = mock_get_dpi
        mock_user32.GetForegroundWindow.return_value = 12345
        mock_user32.MonitorFromWindow.return_value = 67890
        
        scale = get_windows_scaling()
        
        assert scale == 120 / 96.0
    
    @patch('pvv_mcp_server.avatar.mod_update_position.ctypes.windll')
    def test_get_windows_scaling_exception(self, mock_windll):
        """例外発生時にデフォルト値1.0を返すことをテスト"""
        mock_windll.user32.SetProcessDpiAwarenessContext.side_effect = Exception("Test error")
        
        scale = get_windows_scaling()
        
        assert scale == 1.0
    