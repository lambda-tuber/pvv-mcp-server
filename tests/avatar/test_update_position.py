"""
test_update_position.py
mod_update_position.pyのユニットテスト
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication, QWidget

# テスト対象モジュールのインポート
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pvv_mcp_server', 'avatar'))
from pvv_mcp_server.avatar.mod_update_position import update_position


class TestUpdatePosition:
    """update_position関数のテストクラス"""
    
    @pytest.fixture(scope="class")
    def qapp(self):
        """QApplicationインスタンスを作成（GUIテストに必要）"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
    
    @pytest.fixture
    def mock_self(self, qapp):
        """AvatarWindowのモックインスタンス"""
        mock = Mock(spec=QWidget)
        mock.app_title = "Claude"
        mock.position = "left_out"
        mock.width = MagicMock(return_value=200)
        mock.height = MagicMock(return_value=400)
        mock.move = MagicMock()
        return mock
    
    @pytest.fixture
    def mock_window(self):
        """pygetwindowのウィンドウモック"""
        window = Mock()
        window.left = 100
        window.top = 100
        window.width = 800
        window.height = 600
        return window
    
    def test_update_position_left_out(self, mock_self, mock_window):
        """left_out位置のテスト"""
        mock_self.position = "left_out"
        
        with patch('pygetwindow.getWindowsWithTitle', return_value=[mock_window]):
            update_position(mock_self)
        
        # 期待される座標: (100 - 200, 100 + 600 - 400) = (-100, 300)
        mock_self.move.assert_called_once_with(-100, 300)
    
    def test_update_position_left_in(self, mock_self, mock_window):
        """left_in位置のテスト"""
        mock_self.position = "left_in"
        
        with patch('pygetwindow.getWindowsWithTitle', return_value=[mock_window]):
            update_position(mock_self)
        
        # 期待される座標: (100, 100 + 600 - 400) = (100, 300)
        mock_self.move.assert_called_once_with(100, 300)
    
    def test_update_position_right_in(self, mock_self, mock_window):
        """right_in位置のテスト"""
        mock_self.position = "right_in"
        
        with patch('pygetwindow.getWindowsWithTitle', return_value=[mock_window]):
            update_position(mock_self)
        
        # 期待される座標: (100 + 800 - 200, 100 + 600 - 400) = (700, 300)
        mock_self.move.assert_called_once_with(700, 300)
    
    def test_update_position_right_out(self, mock_self, mock_window):
        """right_out位置のテスト"""
        mock_self.position = "right_out"
        
        with patch('pygetwindow.getWindowsWithTitle', return_value=[mock_window]):
            update_position(mock_self)
        
        # 期待される座標: (100 + 800, 100 + 600 - 400) = (900, 300)
        mock_self.move.assert_called_once_with(900, 300)
    
    def test_update_position_no_app_title(self, mock_self, mock_window):
        """app_titleが存在しない場合のテスト"""
        delattr(mock_self, 'app_title')
        
        with patch('pygetwindow.getWindowsWithTitle', return_value=[mock_window]):
            update_position(mock_self)
        
        # moveが呼ばれないことを確認
        mock_self.move.assert_not_called()
    
    def test_update_position_empty_app_title(self, mock_self, mock_window):
        """app_titleが空の場合のテスト"""
        mock_self.app_title = ""
        
        with patch('pygetwindow.getWindowsWithTitle', return_value=[mock_window]):
            update_position(mock_self)
        
        # moveが呼ばれないことを確認
        mock_self.move.assert_not_called()
    
    def test_update_position_no_position(self, mock_self, mock_window):
        """positionが存在しない場合のテスト（デフォルト値使用）"""
        delattr(mock_self, 'position')
        
        with patch('pygetwindow.getWindowsWithTitle', return_value=[mock_window]):
            update_position(mock_self)
        
        # デフォルト値 "left_out" が使用される
        # 期待される座標: (100 - 200, 100 + 600 - 400) = (-100, 300)
        mock_self.move.assert_called_once_with(-100, 300)
        assert mock_self.position == "left_out"
    
    def test_update_position_window_not_found(self, mock_self):
        """ターゲットウィンドウが見つからない場合のテスト"""
        with patch('pygetwindow.getWindowsWithTitle', return_value=[]):
            update_position(mock_self)
        
        # moveが呼ばれないことを確認
        mock_self.move.assert_not_called()
    
    def test_update_position_invalid_position(self, mock_self, mock_window):
        """無効なposition値の場合のテスト"""
        mock_self.position = "invalid_position"
        
        with patch('pygetwindow.getWindowsWithTitle', return_value=[mock_window]):
            update_position(mock_self)
        
        # moveが呼ばれないことを確認
        mock_self.move.assert_not_called()
    
    def test_update_position_exception_handling(self, mock_self):
        """例外が発生した場合のテスト"""
        with patch('pygetwindow.getWindowsWithTitle', side_effect=Exception("Test error")):
            # 例外が発生してもクラッシュしない
            update_position(mock_self)
        
        # moveが呼ばれないことを確認
        mock_self.move.assert_not_called()
    
    def test_update_position_multiple_windows(self, mock_self, mock_window):
        """複数のウィンドウが見つかった場合のテスト（最初のウィンドウを使用）"""
        mock_window2 = Mock()
        mock_window2.left = 500
        mock_window2.top = 500
        mock_window2.width = 800
        mock_window2.height = 600
        
        with patch('pygetwindow.getWindowsWithTitle', return_value=[mock_window, mock_window2]):
            update_position(mock_self)
        
        # 最初のウィンドウ (mock_window) の座標が使用される
        # 期待される座標: (100 - 200, 100 + 600 - 400) = (-100, 300)
        mock_self.move.assert_called_once_with(-100, 300)
    
    def test_update_position_different_sizes(self, qapp):
        """異なるサイズのアバターウィンドウでのテスト"""
        mock = Mock(spec=QWidget)
        mock.app_title = "Claude"
        mock.position = "right_out"
        mock.width = MagicMock(return_value=150)  # 幅150
        mock.height = MagicMock(return_value=300)  # 高さ300
        mock.move = MagicMock()
        
        mock_window = Mock()
        mock_window.left = 200
        mock_window.top = 200
        mock_window.width = 1000
        mock_window.height = 800
        
        with patch('pygetwindow.getWindowsWithTitle', return_value=[mock_window]):
            update_position(mock)
        
        # 期待される座標: (200 + 1000, 200 + 800 - 300) = (1200, 700)
        mock.move.assert_called_once_with(1200, 700)

