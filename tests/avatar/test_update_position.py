"""
test_update_position.py
mod_update_positionのUnitTest
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication
import sys

from pvv_mcp_server.avatar.mod_update_position import update_position, get_windows_scaling


class TestGetWindowsScaling:
    """get_windows_scaling関数のテストクラス"""
    
    def test_get_windows_scaling_success(self):
        """DPIスケーリング取得成功のテスト"""
        with patch('ctypes.windll') as mock_windll:
            # モックの設定
            mock_user32 = Mock()
            mock_shcore = Mock()
            mock_windll.user32 = mock_user32
            mock_windll.shcore = mock_shcore
            
            # GetForegroundWindow, MonitorFromWindowのモック
            mock_user32.GetForegroundWindow.return_value = 12345
            mock_user32.MonitorFromWindow.return_value = 67890
            
            # GetDpiForMonitorのモック（120 DPI = 125%スケール）
            def mock_get_dpi(monitor, dpi_type, dpiX, dpiY):
                dpiX._obj.value = 120
                dpiY._obj.value = 120
                return 0
            
            mock_shcore.GetDpiForMonitor.side_effect = mock_get_dpi
            
            # 実行
            scale = get_windows_scaling()
            
            # 検証（120 / 96 = 1.25）
            assert scale == 1.25
    
    def test_get_windows_scaling_exception(self):
        """DPIスケーリング取得失敗時のデフォルト値テスト"""
        with patch('ctypes.windll') as mock_windll:
            # 例外を発生させる
            mock_windll.user32.GetForegroundWindow.side_effect = Exception("Test error")
            
            # 実行
            scale = get_windows_scaling()
            
            # デフォルト値1.0が返されることを検証
            assert scale == 1.0


class TestUpdatePosition:
    """update_position関数のテストクラス"""
    
    @pytest.fixture
    def qapp(self):
        """QApplicationのフィクスチャ"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
    
    @pytest.fixture
    def mock_avatar_window(self):
        """AvatarWindowのモックインスタンス"""
        window = Mock()
        window.app_title = "Claude"
        window.position = "left_out"
        window.width.return_value = 300
        window.height.return_value = 400
        window.move = Mock()
        return window
    
    @pytest.fixture
    def mock_target_window(self):
        """ターゲットウィンドウのモック"""
        target = Mock()
        target.left = 1000
        target.top = 200
        target.width = 800
        target.height = 600
        return target
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_left_out(self, mock_scaling, mock_get_windows, 
                                      mock_avatar_window, mock_target_window, qapp):
        """left_out位置への移動テスト"""
        # モックの設定
        mock_get_windows.return_value = [mock_target_window]
        mock_scaling.return_value = 1.0  # スケーリングなし
        mock_avatar_window.position = "left_out"
        
        # 実行
        update_position(mock_avatar_window)
        
        # 検証（ターゲットの左外側）
        # new_x = 1000 - 300 = 700
        # new_y = 200 + 600 - 400 = 400
        mock_avatar_window.move.assert_called_once_with(700, 400)
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_left_in(self, mock_scaling, mock_get_windows, 
                                     mock_avatar_window, mock_target_window, qapp):
        """left_in位置への移動テスト"""
        mock_get_windows.return_value = [mock_target_window]
        mock_scaling.return_value = 1.0
        mock_avatar_window.position = "left_in"
        
        update_position(mock_avatar_window)
        
        # new_x = 1000
        # new_y = 200 + 600 - 400 = 400
        mock_avatar_window.move.assert_called_once_with(1000, 400)
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_right_in(self, mock_scaling, mock_get_windows, 
                                      mock_avatar_window, mock_target_window, qapp):
        """right_in位置への移動テスト"""
        mock_get_windows.return_value = [mock_target_window]
        mock_scaling.return_value = 1.0
        mock_avatar_window.position = "right_in"
        
        update_position(mock_avatar_window)
        
        # new_x = 1000 + 800 - 300 = 1500
        # new_y = 200 + 600 - 400 = 400
        mock_avatar_window.move.assert_called_once_with(1500, 400)
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_right_out(self, mock_scaling, mock_get_windows, 
                                       mock_avatar_window, mock_target_window, qapp):
        """right_out位置への移動テスト"""
        mock_get_windows.return_value = [mock_target_window]
        mock_scaling.return_value = 1.0
        mock_avatar_window.position = "right_out"
        
        update_position(mock_avatar_window)
        
        # new_x = 1000 + 800 = 1800
        # new_y = 200 + 600 - 400 = 400
        mock_avatar_window.move.assert_called_once_with(1800, 400)
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_with_scaling(self, mock_scaling, mock_get_windows, 
                                          mock_avatar_window, mock_target_window, qapp):
        """DPIスケーリング125%の場合のテスト"""
        mock_get_windows.return_value = [mock_target_window]
        mock_scaling.return_value = 1.25  # 125%スケール
        mock_avatar_window.position = "left_out"
        
        # ターゲットウィンドウの論理座標
        mock_target_window.left = 1250
        mock_target_window.top = 250
        mock_target_window.width = 1000
        mock_target_window.height = 750
        
        update_position(mock_avatar_window)
        
        # スケーリング補正後の座標計算
        # target_x = 1250 / 1.25 = 1000
        # target_y = 250 / 1.25 = 200
        # target_width = 1000 / 1.25 = 800
        # target_height = 750 / 1.25 = 600
        # new_x = 1000 - 300 = 700
        # new_y = 200 + 600 - 400 = 400
        mock_avatar_window.move.assert_called_once_with(700, 400)
    
    def test_update_position_no_app_title(self, mock_avatar_window, qapp):
        """app_titleが設定されていない場合のテスト"""
        mock_avatar_window.app_title = None
        
        # 実行（例外が発生しないことを確認）
        update_position(mock_avatar_window)
        
        # moveが呼ばれないことを検証
        mock_avatar_window.move.assert_not_called()
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    def test_update_position_window_not_found(self, mock_get_windows, 
                                              mock_avatar_window, qapp):
        """ターゲットウィンドウが見つからない場合のテスト"""
        mock_get_windows.return_value = []  # ウィンドウが見つからない
        
        # 実行
        update_position(mock_avatar_window)
        
        # moveが呼ばれないことを検証
        mock_avatar_window.move.assert_not_called()
    
    def test_update_position_no_position_attribute(self, mock_avatar_window, qapp):
        """position属性がない場合のデフォルト値テスト"""
        delattr(mock_avatar_window, 'position')
        
        with patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle') as mock_get_windows:
            mock_target = Mock()
            mock_target.left = 1000
            mock_target.top = 200
            mock_target.width = 800
            mock_target.height = 600
            mock_get_windows.return_value = [mock_target]
            
            with patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling', return_value=1.0):
                update_position(mock_avatar_window)
                
                # デフォルトのleft_outで配置されることを検証
                assert hasattr(mock_avatar_window, 'position')
                assert mock_avatar_window.position == "left_out"
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_windows_scaling')
    def test_update_position_unknown_position(self, mock_scaling, mock_get_windows, 
                                              mock_avatar_window, mock_target_window, qapp):
        """不正なposition値の場合のテスト"""
        mock_get_windows.return_value = [mock_target_window]
        mock_scaling.return_value = 1.0
        mock_avatar_window.position = "invalid_position"
        
        # 実行
        update_position(mock_avatar_window)
        
        # moveが呼ばれないことを検証
        mock_avatar_window.move.assert_not_called()
    
    @patch('pvv_mcp_server.avatar.mod_update_position.gw.getWindowsWithTitle')
    def test_update_position_exception_handling(self, mock_get_windows, 
                                                mock_avatar_window, qapp):
        """例外発生時のハンドリングテスト"""
        # getWindowsWithTitleで例外を発生させる
        mock_get_windows.side_effect = Exception("Test exception")
        
        # 実行（例外が外に漏れないことを確認）
        update_position(mock_avatar_window)
        
        # moveが呼ばれないことを検証
        mock_avatar_window.move.assert_not_called()