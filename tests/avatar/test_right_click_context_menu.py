# tests/avatar/test_right_click_context_menu.py
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import QPoint, QTimer
from pvv_mcp_server.avatar.mod_right_click_context_menu import right_click_context_menu


class TestRightClickContextMenu:
    """right_click_context_menu関数のユニットテスト"""

    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    def test_context_menu_with_animations(self, mock_qaction_class, mock_qmenu_class):
        """正常系: アニメーション登録ありのコンテキストメニュー表示"""
        # Arrange
        mock_self = Mock()
        mock_position = Mock(spec=QPoint)
        
        # pixmap_dictの設定
        mock_self.pixmap_dict = {
            "立ち絵": {},
            "口パク": {},
            "まばたき": {}
        }
        mock_self.frame_timer_interval = 100
        mock_self.position = "left_out"
        mock_self.flip = False
        
        # follow_timerのモック
        mock_follow_timer = Mock(spec=QTimer)
        mock_follow_timer.isActive.return_value = True
        mock_self.follow_timer = mock_follow_timer
        
        # QMenuのモック
        mock_menu = Mock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        # サブメニューのモック
        mock_animation_menu = Mock()
        mock_speed_menu = Mock()
        mock_position_menu = Mock()
        mock_follow_menu = Mock()
        
        mock_menu.addMenu.side_effect = [
            mock_animation_menu,
            mock_speed_menu,
            mock_position_menu,
            mock_follow_menu
        ]
        
        # QActionのモック
        mock_actions = []
        for i in range(20):  # 十分な数のアクションを用意
            mock_action = Mock(spec=QAction)
            mock_actions.append(mock_action)
        mock_qaction_class.side_effect = mock_actions
        
        # mapToGlobalのモック
        mock_global_pos = Mock()
        mock_self.mapToGlobal.return_value = mock_global_pos
        
        # Act
        right_click_context_menu(mock_self, mock_position)
        
        # Assert
        # メニューが作成されたことを確認
        mock_qmenu_class.assert_called_once_with(mock_self)
        
        # サブメニューが追加されたことを確認
        assert mock_menu.addMenu.call_count == 4
        menu_calls = [call[0][0] for call in mock_menu.addMenu.call_args_list]
        assert "アニメーション" in menu_calls
        assert "アニメーション速度" in menu_calls
        assert "表示位置" in menu_calls
        assert "位置追随" in menu_calls
        
        # アニメーションメニューにアクションが追加されたことを確認
        assert mock_animation_menu.addAction.call_count >= 3  # 3つのアニメーション
        
        # メニューが表示されたことを確認
        mock_menu.exec.assert_called_once_with(mock_global_pos)

    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    def test_context_menu_without_animations(self, mock_qaction_class, mock_qmenu_class):
        """正常系: アニメーション登録なしのコンテキストメニュー表示"""
        # Arrange
        mock_self = Mock()
        mock_position = Mock(spec=QPoint)
        
        # pixmap_dictが空
        mock_self.pixmap_dict = {}
        mock_self.frame_timer_interval = 150
        mock_self.position = "right_in"
        mock_self.flip = True
        
        mock_follow_timer = Mock(spec=QTimer)
        mock_follow_timer.isActive.return_value = False
        mock_self.follow_timer = mock_follow_timer
        
        # QMenuのモック
        mock_menu = Mock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        # サブメニューのモック
        mock_animation_menu = Mock()
        mock_speed_menu = Mock()
        mock_position_menu = Mock()
        mock_follow_menu = Mock()
        
        mock_menu.addMenu.side_effect = [
            mock_animation_menu,
            mock_speed_menu,
            mock_position_menu,
            mock_follow_menu
        ]
        
        # QActionのモック
        mock_actions = []
        for i in range(20):
            mock_action = Mock(spec=QAction)
            mock_actions.append(mock_action)
        mock_qaction_class.side_effect = mock_actions
        
        mock_global_pos = Mock()
        mock_self.mapToGlobal.return_value = mock_global_pos
        
        # Act
        right_click_context_menu(mock_self, mock_position)
        
        # Assert
        # アニメーションメニューには「(なし)」が追加される
        no_anime_action = mock_actions[0]
        no_anime_action.setEnabled.assert_called_once_with(False)
        mock_animation_menu.addAction.assert_called()

    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    def test_context_menu_speed_settings(self, mock_qaction_class, mock_qmenu_class):
        """正常系: アニメーション速度設定の確認"""
        # Arrange
        mock_self = Mock()
        mock_position = Mock(spec=QPoint)
        
        mock_self.pixmap_dict = {"立ち絵": {}}
        mock_self.frame_timer_interval = 200  # 低速
        mock_self.position = "left_out"
        mock_self.flip = False
        
        mock_follow_timer = Mock(spec=QTimer)
        mock_follow_timer.isActive.return_value = True
        mock_self.follow_timer = mock_follow_timer
        
        mock_menu = Mock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        mock_animation_menu = Mock()
        mock_speed_menu = Mock()
        mock_position_menu = Mock()
        mock_follow_menu = Mock()
        
        mock_menu.addMenu.side_effect = [
            mock_animation_menu,
            mock_speed_menu,
            mock_position_menu,
            mock_follow_menu
        ]
        
        mock_actions = []
        for i in range(20):
            mock_action = Mock(spec=QAction)
            mock_actions.append(mock_action)
        mock_qaction_class.side_effect = mock_actions
        
        mock_global_pos = Mock()
        mock_self.mapToGlobal.return_value = mock_global_pos
        
        # Act
        right_click_context_menu(mock_self, mock_position)
        
        # Assert
        # 速度メニューに5つのアクションが追加される
        assert mock_speed_menu.addAction.call_count == 5
        
        # 各速度設定アクションがチェック可能であることを確認
        speed_actions = mock_actions[1:6]  # 最初のアクションはアニメーション用
        for action in speed_actions:
            action.setCheckable.assert_called_once_with(True)

    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    def test_context_menu_position_settings(self, mock_qaction_class, mock_qmenu_class):
        """正常系: 表示位置設定の確認"""
        # Arrange
        mock_self = Mock()
        mock_position = Mock(spec=QPoint)
        
        mock_self.pixmap_dict = {"立ち絵": {}}
        mock_self.frame_timer_interval = 100
        mock_self.position = "right_out"  # 右下外側
        mock_self.flip = False
        
        mock_follow_timer = Mock(spec=QTimer)
        mock_follow_timer.isActive.return_value = True
        mock_self.follow_timer = mock_follow_timer
        
        mock_menu = Mock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        mock_animation_menu = Mock()
        mock_speed_menu = Mock()
        mock_position_menu = Mock()
        mock_follow_menu = Mock()
        
        mock_menu.addMenu.side_effect = [
            mock_animation_menu,
            mock_speed_menu,
            mock_position_menu,
            mock_follow_menu
        ]
        
        mock_actions = []
        for i in range(20):
            mock_action = Mock(spec=QAction)
            mock_actions.append(mock_action)
        mock_qaction_class.side_effect = mock_actions
        
        mock_global_pos = Mock()
        mock_self.mapToGlobal.return_value = mock_global_pos
        
        # Act
        right_click_context_menu(mock_self, mock_position)
        
        # Assert
        # 表示位置メニューに4つのアクションが追加される
        assert mock_position_menu.addAction.call_count == 4

    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    def test_context_menu_flip_setting(self, mock_qaction_class, mock_qmenu_class):
        """正常系: 左右反転設定の確認"""
        # Arrange
        mock_self = Mock()
        mock_position = Mock(spec=QPoint)
        
        mock_self.pixmap_dict = {"立ち絵": {}}
        mock_self.frame_timer_interval = 100
        mock_self.position = "left_out"
        mock_self.flip = True  # 反転有効
        
        mock_follow_timer = Mock(spec=QTimer)
        mock_follow_timer.isActive.return_value = True
        mock_self.follow_timer = mock_follow_timer
        
        mock_menu = Mock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        mock_animation_menu = Mock()
        mock_speed_menu = Mock()
        mock_position_menu = Mock()
        mock_follow_menu = Mock()
        
        mock_menu.addMenu.side_effect = [
            mock_animation_menu,
            mock_speed_menu,
            mock_position_menu,
            mock_follow_menu
        ]
        
        mock_actions = []
        for i in range(20):
            mock_action = Mock(spec=QAction)
            mock_actions.append(mock_action)
        mock_qaction_class.side_effect = mock_actions
        
        mock_global_pos = Mock()
        mock_self.mapToGlobal.return_value = mock_global_pos
        
        # Act
        right_click_context_menu(mock_self, mock_position)
        
        # Assert
        # 左右反転アクションが追加される
        assert mock_menu.addAction.call_count >= 1

    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    def test_context_menu_follow_settings(self, mock_qaction_class, mock_qmenu_class):
        """正常系: 位置追随設定の確認"""
        # Arrange
        mock_self = Mock()
        mock_position = Mock(spec=QPoint)
        
        mock_self.pixmap_dict = {"立ち絵": {}}
        mock_self.frame_timer_interval = 100
        mock_self.position = "left_out"
        mock_self.flip = False
        
        # 位置追随がOFFの状態
        mock_follow_timer = Mock(spec=QTimer)
        mock_follow_timer.isActive.return_value = False
        mock_self.follow_timer = mock_follow_timer
        
        mock_menu = Mock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        mock_animation_menu = Mock()
        mock_speed_menu = Mock()
        mock_position_menu = Mock()
        mock_follow_menu = Mock()
        
        mock_menu.addMenu.side_effect = [
            mock_animation_menu,
            mock_speed_menu,
            mock_position_menu,
            mock_follow_menu
        ]
        
        mock_actions = []
        for i in range(20):
            mock_action = Mock(spec=QAction)
            mock_actions.append(mock_action)
        mock_qaction_class.side_effect = mock_actions
        
        mock_global_pos = Mock()
        mock_self.mapToGlobal.return_value = mock_global_pos
        
        # Act
        right_click_context_menu(mock_self, mock_position)
        
        # Assert
        # 位置追随メニューに2つのアクション(ON/OFF)が追加される
        assert mock_follow_menu.addAction.call_count == 2

    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    def test_context_menu_no_pixmap_dict_attribute(self, mock_qaction_class, mock_qmenu_class):
        """異常系: pixmap_dict属性が存在しない場合"""
        # Arrange
        mock_self = Mock()  # spec指定を外す
        mock_position = Mock(spec=QPoint)
        
        # pixmap_dictを削除
        if hasattr(mock_self, 'pixmap_dict'):
            delattr(mock_self, 'pixmap_dict')
        
        mock_self.frame_timer_interval = 100
        mock_self.position = "left_out"
        mock_self.flip = False
        
        mock_follow_timer = Mock(spec=QTimer)
        mock_follow_timer.isActive.return_value = True
        mock_self.follow_timer = mock_follow_timer
        
        mock_menu = Mock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        mock_animation_menu = Mock()
        mock_speed_menu = Mock()
        mock_position_menu = Mock()
        mock_follow_menu = Mock()
        
        mock_menu.addMenu.side_effect = [
            mock_animation_menu,
            mock_speed_menu,
            mock_position_menu,
            mock_follow_menu
        ]
        
        mock_actions = []
        for i in range(20):
            mock_action = Mock(spec=QAction)
            mock_actions.append(mock_action)
        mock_qaction_class.side_effect = mock_actions
        
        # mapToGlobalのモックを追加
        mock_global_pos = Mock()
        mock_self.mapToGlobal.return_value = mock_global_pos
        
        # Act
        right_click_context_menu(mock_self, mock_position)
        
        # Assert
        # 例外が発生せず、メニューが表示されることを確認
        mock_menu.exec.assert_called_once()

    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    def test_context_menu_default_values(self, mock_qaction_class, mock_qmenu_class):
        """正常系: デフォルト値での動作確認"""
        # Arrange
        mock_self = Mock()
        mock_position = Mock(spec=QPoint)
        
        mock_self.pixmap_dict = {"立ち絵": {}}
        # frame_timer_intervalがない場合、デフォルト100が使われる
        delattr(mock_self, 'frame_timer_interval')
        # positionがない場合、デフォルト'left_out'が使われる
        delattr(mock_self, 'position')
        mock_self.flip = False
        
        mock_follow_timer = Mock(spec=QTimer)
        mock_follow_timer.isActive.return_value = True
        mock_self.follow_timer = mock_follow_timer
        
        mock_menu = Mock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        mock_animation_menu = Mock()
        mock_speed_menu = Mock()
        mock_position_menu = Mock()
        mock_follow_menu = Mock()
        
        mock_menu.addMenu.side_effect = [
            mock_animation_menu,
            mock_speed_menu,
            mock_position_menu,
            mock_follow_menu
        ]
        
        mock_actions = []
        for i in range(20):
            mock_action = Mock(spec=QAction)
            mock_actions.append(mock_action)
        mock_qaction_class.side_effect = mock_actions
        
        mock_global_pos = Mock()
        mock_self.mapToGlobal.return_value = mock_global_pos
        
        # Act
        right_click_context_menu(mock_self, mock_position)
        
        # Assert
        # デフォルト値で処理されることを確認
        mock_menu.exec.assert_called_once()
