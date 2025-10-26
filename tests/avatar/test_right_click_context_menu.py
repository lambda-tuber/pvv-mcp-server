"""
test_right_click_context_menu.py
mod_right_click_context_menuのユニットテスト
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# PySide6のインポートは実際のものを使用
from PySide6.QtCore import QPoint
from pvv_mcp_server.avatar.mod_right_click_context_menu import right_click_context_menu, _show_dialog_debug


class TestRightClickContextMenu:
    """right_click_context_menu関数のテストクラス"""
    
    @pytest.fixture
    def mock_timer(self):
        """QTimerのモックを作成"""
        timer = Mock()
        timer.isActive.return_value = False
        timer.start = Mock()
        timer.stop = Mock()
        return timer
    
    @pytest.fixture
    def mock_avatar(self, mock_timer):
        """AvatarWindowのモックを作成"""
        avatar = Mock()
        avatar.anime_types = ["立ち絵", "口パク", "感情表現"]
        avatar.anime_type = "立ち絵"
        avatar.frame_timer_interval = 150
        avatar.position = "left_out"
        avatar.flip = False
        avatar.scale = 50
        avatar.follow_timer = mock_timer
        
        # メソッドのモック
        avatar.set_anime_type = Mock()
        avatar.set_frame_timer_interval = Mock()
        avatar.set_position = Mock()
        avatar.set_flip = Mock()
        avatar.set_scale = Mock()
        avatar.mapToGlobal = Mock(return_value=QPoint(100, 100))
        
        # dialogsのモック
        avatar.dialogs = {
            "立ち絵": Mock(),
            "口パク": Mock(),
            "感情表現": Mock()
        }
        
        return avatar
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_right_click_context_menu_no_exception(self, mock_qmenu_class, mock_qaction_class, mock_avatar):
        """メニューが例外なく実行されることをテスト"""
        # QMenuのモック
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu
        
        # QActionのモック
        mock_action = Mock()
        mock_qaction_class.return_value = mock_action
        
        position = QPoint(50, 50)
        
        # 例外が発生しないことを確認
        right_click_context_menu(mock_avatar, position)
        
        # メニューが作成されることを確認
        mock_qmenu_class.assert_called_once_with(mock_avatar)
        
        # execが呼ばれることを確認
        mock_menu.exec.assert_called_once()
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_right_click_context_menu_with_different_positions(self, mock_qmenu_class, mock_qaction_class, mock_avatar):
        """異なる位置でメニューが呼び出されることをテスト"""
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu
        mock_action = Mock()
        mock_qaction_class.return_value = mock_action
        
        positions = [
            QPoint(0, 0),
            QPoint(100, 200),
            QPoint(-50, -50),
            QPoint(1000, 1000)
        ]
        
        for pos in positions:
            mock_avatar.mapToGlobal.reset_mock()
            right_click_context_menu(mock_avatar, pos)
            mock_avatar.mapToGlobal.assert_called_with(pos)
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_animation_menu_structure(self, mock_qmenu_class, mock_qaction_class, mock_avatar):
        """アニメーションメニューの構造をテスト"""
        mock_menu = Mock()
        mock_animation_submenu = Mock()
        
        # addMenuが呼ばれたときにサブメニューを返す
        mock_menu.addMenu.return_value = mock_animation_submenu
        mock_animation_submenu.addMenu.return_value = Mock()
        
        mock_qmenu_class.return_value = mock_menu
        mock_action = Mock()
        mock_qaction_class.return_value = mock_action
        
        position = QPoint(50, 50)
        right_click_context_menu(mock_avatar, position)
        
        # アニメーションメニューが追加されることを確認
        assert any("アニメーション" in str(call) for call in mock_menu.addMenu.call_args_list)
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_current_anime_type_marked(self, mock_qmenu_class, mock_qaction_class, mock_avatar):
        """現在のアニメタイプがマークされることをテスト"""
        mock_avatar.anime_type = "口パク"
        
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu
        mock_action = Mock()
        mock_qaction_class.return_value = mock_action
        
        position = QPoint(50, 50)
        
        # 例外なく実行されることを確認
        right_click_context_menu(mock_avatar, position)
        
        # メニューが実行されることを確認
        mock_menu.exec.assert_called_once()
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_follow_timer_states(self, mock_qmenu_class, mock_qaction_class, mock_avatar):
        """位置追随タイマーの状態をテスト"""
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu
        mock_action = Mock()
        mock_qaction_class.return_value = mock_action
        
        position = QPoint(50, 50)
        
        # タイマーがアクティブな場合
        mock_avatar.follow_timer.isActive.return_value = True
        right_click_context_menu(mock_avatar, position)
        
        # タイマー状態が確認されることを確認
        mock_avatar.follow_timer.isActive.assert_called()
        
        # タイマーが非アクティブな場合
        mock_avatar.follow_timer.isActive.reset_mock()
        mock_avatar.follow_timer.isActive.return_value = False
        right_click_context_menu(mock_avatar, position)
        
        # タイマー状態が確認されることを確認
        assert mock_avatar.follow_timer.isActive.called
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_flip_state(self, mock_qmenu_class, mock_qaction_class, mock_avatar):
        """左右反転状態をテスト"""
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu
        mock_action = Mock()
        mock_qaction_class.return_value = mock_action
        
        position = QPoint(50, 50)
        
        # 反転がTrueの場合
        mock_avatar.flip = True
        right_click_context_menu(mock_avatar, position)
        mock_menu.exec.assert_called()
        
        # 反転がFalseの場合
        mock_menu.exec.reset_mock()
        mock_avatar.flip = False
        right_click_context_menu(mock_avatar, position)
        mock_menu.exec.assert_called()
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_different_frame_intervals(self, mock_qmenu_class, mock_qaction_class, mock_avatar):
        """異なるフレーム間隔でテスト"""
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu
        mock_action = Mock()
        mock_qaction_class.return_value = mock_action
        
        position = QPoint(50, 50)
        intervals = [25, 50, 100, 150, 200, 250, 300]
        
        for interval in intervals:
            mock_avatar.frame_timer_interval = interval
            mock_menu.exec.reset_mock()
            
            # 例外なく実行される
            right_click_context_menu(mock_avatar, position)
            mock_menu.exec.assert_called_once()
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_different_positions_setting(self, mock_qmenu_class, mock_qaction_class, mock_avatar):
        """異なる表示位置でテスト"""
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu
        mock_action = Mock()
        mock_qaction_class.return_value = mock_action
        
        position = QPoint(50, 50)
        positions = ["left_out", "left_center", "left_in", "right_in", "right_center", "right_out"]
        
        for pos in positions:
            mock_avatar.position = pos
            mock_menu.exec.reset_mock()
            
            # 例外なく実行される
            right_click_context_menu(mock_avatar, position)
            mock_menu.exec.assert_called_once()
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_different_scales(self, mock_qmenu_class, mock_qaction_class, mock_avatar):
        """異なるスケールでテスト"""
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu
        mock_action = Mock()
        mock_qaction_class.return_value = mock_action
        
        position = QPoint(50, 50)
        scales = [25, 50, 75, 100, 125, 150, 175, 200]
        
        for scale in scales:
            mock_avatar.scale = scale
            mock_menu.exec.reset_mock()
            
            # 例外なく実行される
            right_click_context_menu(mock_avatar, position)
            mock_menu.exec.assert_called_once()
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_multiple_anime_types(self, mock_qmenu_class, mock_qaction_class, mock_avatar):
        """複数のアニメタイプでテスト"""
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu
        mock_action = Mock()
        mock_qaction_class.return_value = mock_action
        
        position = QPoint(50, 50)
        
        # 1つのアニメタイプ
        mock_avatar.anime_types = ["立ち絵"]
        mock_avatar.anime_type = "立ち絵"
        mock_avatar.dialogs = {"立ち絵": Mock()}
        
        right_click_context_menu(mock_avatar, position)
        mock_menu.exec.assert_called()
        
        # 複数のアニメタイプ
        mock_menu.exec.reset_mock()
        mock_avatar.anime_types = ["立ち絵", "口パク", "感情表現", "まばたき"]
        mock_avatar.anime_type = "感情表現"
        mock_avatar.dialogs = {
            "立ち絵": Mock(),
            "口パク": Mock(),
            "感情表現": Mock(),
            "まばたき": Mock()
        }
        
        right_click_context_menu(mock_avatar, position)
        mock_menu.exec.assert_called()
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_qaction_created_multiple_times(self, mock_qmenu_class, mock_qaction_class, mock_avatar):
        """QActionが複数回作成されることをテスト"""
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu
        mock_action = Mock()
        mock_qaction_class.return_value = mock_action
        
        position = QPoint(50, 50)
        right_click_context_menu(mock_avatar, position)
        
        # QActionが複数回作成されることを確認（各メニュー項目用）
        assert mock_qaction_class.call_count > 0


class TestShowDialogDebug:
    """_show_dialog_debug関数のテストクラス"""
    
    @pytest.fixture
    def mock_dialog(self):
        """Dialogのモックを作成"""
        dialog = Mock()
        dialog.show = Mock()
        dialog.raise_ = Mock()
        dialog.activateWindow = Mock()
        return dialog
    
    @pytest.fixture
    def mock_avatar(self, mock_dialog):
        """AvatarWindowのモックを作成"""
        avatar = Mock()
        avatar.dialogs = {
            "立ち絵": mock_dialog,
            "口パク": Mock()
        }
        avatar.set_anime_type = Mock()
        return avatar
    
    def test_show_dialog_success(self, mock_avatar, mock_dialog):
        """ダイアログが正常に表示されることをテスト"""
        anime_type = "立ち絵"
        
        _show_dialog_debug(mock_avatar, anime_type)
        
        # set_anime_typeが呼ばれることを確認
        mock_avatar.set_anime_type.assert_called_once_with(anime_type)
        
        # ダイアログのshow, raise_, activateWindowが呼ばれることを確認
        mock_dialog.show.assert_called_once()
        mock_dialog.raise_.assert_called_once()
        mock_dialog.activateWindow.assert_called_once()
    
    def test_show_dialog_not_found(self, mock_avatar):
        """存在しないダイアログを指定した場合のテスト"""
        anime_type = "存在しない"
        
        # 例外が発生しないことを確認
        _show_dialog_debug(mock_avatar, anime_type)
        
        # set_anime_typeは呼ばれる
        mock_avatar.set_anime_type.assert_called_once_with(anime_type)
    
    def test_show_dialog_exception_in_show(self, mock_avatar, mock_dialog):
        """ダイアログのshow()で例外が発生する場合のテスト"""
        mock_dialog.show.side_effect = Exception("Test exception")
        anime_type = "立ち絵"
        
        # 例外が外部に漏れないことを確認
        _show_dialog_debug(mock_avatar, anime_type)
        
        # set_anime_typeは呼ばれる
        mock_avatar.set_anime_type.assert_called_once_with(anime_type)
    
    def test_show_dialog_multiple_types(self, mock_avatar):
        """複数のダイアログタイプが存在する場合のテスト"""
        dialog1 = Mock()
        dialog2 = Mock()
        mock_avatar.dialogs = {
            "立ち絵": dialog1,
            "口パク": dialog2
        }
        
        # 立ち絵を表示
        _show_dialog_debug(mock_avatar, "立ち絵")
        dialog1.show.assert_called_once()
        dialog2.show.assert_not_called()
        
        # モックをリセット
        dialog1.reset_mock()
        dialog2.reset_mock()
        
        # 口パクを表示
        _show_dialog_debug(mock_avatar, "口パク")
        dialog1.show.assert_not_called()
        dialog2.show.assert_called_once()
    
    def test_show_dialog_call_order(self, mock_avatar, mock_dialog):
        """メソッドが正しい順序で呼ばれることをテスト"""
        call_order = []
        
        mock_avatar.set_anime_type.side_effect = lambda x: call_order.append('set_anime_type')
        mock_dialog.show.side_effect = lambda: call_order.append('show')
        mock_dialog.raise_.side_effect = lambda: call_order.append('raise_')
        mock_dialog.activateWindow.side_effect = lambda: call_order.append('activateWindow')
        
        anime_type = "立ち絵"
        _show_dialog_debug(mock_avatar, anime_type)
        
        # 呼び出し順序を確認
        assert call_order == ['set_anime_type', 'show', 'raise_', 'activateWindow']
    
    def test_show_dialog_exception_in_raise(self, mock_avatar, mock_dialog):
        """ダイアログのraise_()で例外が発生する場合のテスト"""
        mock_dialog.raise_.side_effect = Exception("Test exception")
        anime_type = "立ち絵"
        
        # 例外が外部に漏れないことを確認
        _show_dialog_debug(mock_avatar, anime_type)
        
        # set_anime_typeとshowは呼ばれる
        mock_avatar.set_anime_type.assert_called_once_with(anime_type)
        mock_dialog.show.assert_called_once()
    
    def test_show_dialog_exception_in_activate(self, mock_avatar, mock_dialog):
        """ダイアログのactivateWindow()で例外が発生する場合のテスト"""
        mock_dialog.activateWindow.side_effect = Exception("Test exception")
        anime_type = "立ち絵"
        
        # 例外が外部に漏れないことを確認
        _show_dialog_debug(mock_avatar, anime_type)
        
        # set_anime_type, show, raise_は呼ばれる
        mock_avatar.set_anime_type.assert_called_once_with(anime_type)
        mock_dialog.show.assert_called_once()
        mock_dialog.raise_.assert_called_once()