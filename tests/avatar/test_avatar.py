import pytest
import sys
from unittest.mock import MagicMock, patch, call
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from pvv_mcp_server.avatar.mod_avatar import AvatarWindow


@pytest.fixture(scope="module")
def qapp():
    """QApplicationのフィクスチャ"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # テスト終了後にクリーンアップはしない(他のテストで使用される可能性)


@pytest.fixture
def mock_dependencies():
    """依存関係をモック化"""
    with patch('pvv_mcp_server.avatar.mod_avatar.load_image') as mock_load_image, \
         patch('pvv_mcp_server.avatar.mod_avatar.update_frame') as mock_update_frame, \
         patch('pvv_mcp_server.avatar.mod_avatar.AvatarDialog') as mock_dialog, \
         patch('pvv_mcp_server.avatar.mod_avatar.pvv_mcp_server.avatar.mod_update_position') as mock_update_pos_module:
        
        # load_imageは空のzip_dataを返す
        mock_load_image.return_value = {
            '後': {}, '体': {}, '顔': {}, '髪': {}, 
            '口': {}, '目': {}, '眉': {}, '他': {}
        }
        
        # AvatarDialogのモックインスタンスを設定
        mock_dialog_instance = MagicMock()
        mock_dialog_instance.save_config.return_value = {
            "parts": {},
            "timer_interval": 50
        }
        mock_dialog.return_value = mock_dialog_instance
        
        # mod_update_position.update_positionのモック
        mock_update_pos_module.update_position = MagicMock()
        
        yield {
            'load_image': mock_load_image,
            'update_frame': mock_update_frame,
            'dialog': mock_dialog,
            'dialog_instance': mock_dialog_instance,
            'update_position_module': mock_update_pos_module
        }


class TestAvatarWindow:
    """AvatarWindowクラスのテストクラス"""
    
    def test_init_basic(self, qapp, mock_dependencies):
        """基本的な初期化のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者",
            zip_path="test.zip",
            app_title="TestApp",
            anime_types=["立ち絵", "口パク"],
            flip=False,
            scale_percent=100,
            position="right_out"
        )
        
        # 基本プロパティの確認
        assert avatar.style_id == 1
        assert avatar.speaker_name == "テスト話者"
        assert avatar.zip_path == "test.zip"
        assert avatar.app_title == "TestApp"
        assert avatar.position == "right_out"
        assert avatar.flip == False
        assert avatar.scale_percent == 100
        assert avatar.anime_types == ["立ち絵", "口パク"]
        assert avatar.anime_type == "立ち絵"
        
        # load_imageが呼ばれたことを確認
        mock_dependencies['load_image'].assert_called_once_with("test.zip", "テスト話者")
        
        # タイマーが開始されていることを確認
        assert avatar.frame_timer.isActive()
        assert avatar.follow_timer.isActive()
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_init_default_anime_types(self, qapp, mock_dependencies):
        """anime_typesがNoneの場合のデフォルト値テスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者"
        )
        
        # デフォルトのanime_typesが設定されていること
        assert avatar.anime_types == ["立ち絵", "口パク"]
        assert avatar.anime_type == "立ち絵"
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_save_config(self, qapp, mock_dependencies):
        """save_config()のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者",
            zip_path="test.zip",
            app_title="TestApp",
            anime_types=["立ち絵", "口パク"],
            flip=True,
            scale_percent=75,
            position="left_in"
        )
        
        config = avatar.save_config()
        
        # 設定が正しく保存されていること
        assert config["zip_path"] == "test.zip"
        assert config["app_title"] == "TestApp"
        assert config["position"] == "left_in"
        assert config["flip"] == True
        assert config["scale"] == 75
        assert config["anime_types"] == ["立ち絵", "口パク"]
        assert "dialogs" in config
        
        # ダイアログの設定も保存されていること
        assert "立ち絵" in config["dialogs"]
        assert "口パク" in config["dialogs"]
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_load_config(self, qapp, mock_dependencies):
        """load_config()のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者"
        )
        
        # 設定を読み込む
        config = {
            "zip_path": "new.zip",
            "app_title": "NewApp",
            "position": "left_out",
            "flip": True,
            "scale": 50,
            "anime_types": ["立ち絵"],
            "frame_timer_interval": 100,
            "follow_timer_interval": 200,
            "dialogs": {
                "立ち絵": {"parts": {}, "timer_interval": 100}
            }
        }
        
        avatar.load_config(config)
        
        # 設定が反映されていること
        assert avatar.zip_path == "new.zip"
        assert avatar.app_title == "NewApp"
        assert avatar.position == "left_out"
        assert avatar.flip == True
        assert avatar.scale_percent == 50
        assert avatar.frame_timer_interval == 100
        
        # ダイアログのload_configが呼ばれたこと
        mock_dependencies['dialog_instance'].load_config.assert_called()
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_set_anime_type(self, qapp, mock_dependencies):
        """set_anime_type()のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者",
            anime_types=["立ち絵", "口パク"]
        )
        
        # アニメーションタイプを変更
        avatar.set_anime_type("口パク")
        
        # anime_typeが変更されていること
        assert avatar.anime_type == "口パク"
        
        # start_oneshotが呼ばれたこと
        mock_dependencies['dialog_instance'].start_oneshot.assert_called()
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_set_anime_type_invalid(self, qapp, mock_dependencies):
        """無効なanime_typeを指定した場合のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者",
            anime_types=["立ち絵", "口パク"]
        )
        
        original_type = avatar.anime_type
        
        # 存在しないanime_typeを指定
        avatar.set_anime_type("存在しない")
        
        # anime_typeが変更されていないこと
        assert avatar.anime_type == original_type
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_set_frame_timer_interval(self, qapp, mock_dependencies):
        """set_frame_timer_interval()のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者"
        )
        
        # 間隔を変更
        avatar.set_frame_timer_interval(200)
        
        # 間隔が変更されていること
        assert avatar.frame_timer_interval == 200
        assert avatar.frame_timer.interval() == 200
        
        # ダイアログの間隔も変更されたこと
        mock_dependencies['dialog_instance'].set_frame_timer_interval.assert_called_with(200)
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_set_position(self, qapp, mock_dependencies):
        """set_position()のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者",
            position="right_out"
        )
        
        # 位置を変更
        avatar.set_position("left_in")
        
        # 位置が変更されていること
        assert avatar.position == "left_in"
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_set_flip(self, qapp, mock_dependencies):
        """set_flip()のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者",
            flip=False
        )
        
        # 反転フラグを変更
        avatar.set_flip(True)
        
        # フラグが変更されていること
        assert avatar.flip == True
        
        # ダイアログの反転フラグも変更されたこと
        mock_dependencies['dialog_instance'].set_flip.assert_called_with(True)
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_set_scale(self, qapp, mock_dependencies):
        """set_scale()のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者",
            scale_percent=100
        )
        
        # スケールを変更
        avatar.set_scale(50)
        
        # スケールが変更されていること
        assert avatar.scale_percent == 50
        
        # ダイアログのスケールも変更されたこと
        mock_dependencies['dialog_instance'].set_scale.assert_called_with(50)
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_update_position(self, qapp, mock_dependencies):
        """update_position()のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者"
        )
        
        # update_positionを呼び出す
        avatar.update_position()
        
        # mod_update_position.update_positionが呼ばれたこと
        mock_dependencies['update_position_module'].update_position.assert_called_with(avatar)
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_mouse_press_event(self, qapp, mock_dependencies):
        """mousePressEvent()のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者"
        )
        
        # follow_timerが動いていることを確認
        assert avatar.follow_timer.isActive()
        
        # 左クリックイベントをシミュレート
        event = MagicMock()
        event.button.return_value = Qt.LeftButton
        event.globalPosition.return_value.toPoint.return_value = QPoint(100, 100)
        
        with patch.object(avatar, 'frameGeometry') as mock_geometry:
            mock_geometry.return_value.topLeft.return_value = QPoint(50, 50)
            avatar.mousePressEvent(event)
        
        # ドラッグ位置が設定されていること
        assert avatar._drag_pos is not None
        
        # follow_timerが停止していること
        assert not avatar.follow_timer.isActive()
        
        # クリーンアップ
        avatar.frame_timer.stop()
    
    def test_mouse_move_event(self, qapp, mock_dependencies):
        """mouseMoveEvent()のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者"
        )
        
        # ドラッグ開始
        avatar._drag_pos = QPoint(50, 50)
        
        # マウス移動イベントをシミュレート
        event = MagicMock()
        event.buttons.return_value = Qt.LeftButton
        event.globalPosition.return_value.toPoint.return_value = QPoint(200, 200)
        
        with patch.object(avatar, 'move') as mock_move:
            avatar.mouseMoveEvent(event)
            
            # moveが呼ばれたこと
            mock_move.assert_called_once()
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_mouse_release_event(self, qapp, mock_dependencies):
        """mouseReleaseEvent()のテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者"
        )
        
        # ドラッグ開始
        avatar._drag_pos = QPoint(50, 50)
        
        # 左ボタンリリースイベントをシミュレート
        event = MagicMock()
        event.button.return_value = Qt.LeftButton
        
        avatar.mouseReleaseEvent(event)
        
        # ドラッグ位置がクリアされていること
        assert avatar._drag_pos is None
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_right_click_context_menu(self, qapp, mock_dependencies):
        """right_click_context_menu()のテスト"""
        with patch('pvv_mcp_server.avatar.mod_avatar.right_click_context_menu') as mock_menu:
            avatar = AvatarWindow(
                style_id=1,
                speaker_name="テスト話者"
            )
            
            # 右クリックメニューを呼び出す
            position = QPoint(100, 100)
            avatar.right_click_context_menu(position)
            
            # right_click_context_menuが呼ばれたこと
            mock_menu.assert_called_once_with(avatar, position)
            
            # クリーンアップ
            avatar.frame_timer.stop()
            avatar.follow_timer.stop()
    
    def test_show_override(self, qapp, mock_dependencies):
        """show()のオーバーライドテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者"
        )
        
        # show()を呼び出す
        avatar.show()
        
        # ウィンドウが表示されていること
        assert avatar.isVisible()
        
        # クリーンアップ
        avatar.hide()
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()
    
    def test_dialogs_created(self, qapp, mock_dependencies):
        """ダイアログが正しく作成されるテスト"""
        avatar = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者",
            anime_types=["立ち絵", "口パク", "瞬き"]
        )
        
        # 各anime_typeに対してダイアログが作成されていること
        assert "立ち絵" in avatar.dialogs
        assert "口パク" in avatar.dialogs
        assert "瞬き" in avatar.dialogs
        
        # AvatarDialogが3回呼ばれたこと
        assert mock_dependencies['dialog'].call_count == 3
        
        # クリーンアップ
        avatar.frame_timer.stop()
        avatar.follow_timer.stop()


class TestAvatarWindowIntegration:
    """統合テスト(モックなし)"""
    
    @patch('pvv_mcp_server.avatar.mod_avatar.load_image')
    @patch('pvv_mcp_server.avatar.mod_avatar.AvatarDialog')
    @patch('pvv_mcp_server.avatar.mod_avatar.pvv_mcp_server.avatar.mod_update_position')
    def test_config_roundtrip(self, mock_update_pos, mock_dialog, mock_load_image, qapp):
        """save_config→load_configのラウンドトリップテスト"""
        # load_imageのモック設定
        mock_load_image.return_value = {
            '後': {}, '体': {}, '顔': {}, '髪': {}, 
            '口': {}, '目': {}, '眉': {}, '他': {}
        }
        
        # AvatarDialogのモック設定
        mock_dialog_instance = MagicMock()
        mock_dialog_instance.save_config.return_value = {"parts": {}}
        mock_dialog.return_value = mock_dialog_instance
        
        # 最初のインスタンスを作成
        avatar1 = AvatarWindow(
            style_id=1,
            speaker_name="テスト話者",
            zip_path="test.zip",
            app_title="TestApp",
            position="right_out",
            flip=True,
            scale_percent=75
        )
        
        # 設定を保存
        config = avatar1.save_config()
        
        # 2つ目のインスタンスを作成して設定を読み込む
        avatar2 = AvatarWindow(
            style_id=2,
            speaker_name="テスト話者2"
        )
        avatar2.load_config(config)
        
        # 設定が正しく反映されていること
        assert avatar2.zip_path == "test.zip"
        assert avatar2.app_title == "TestApp"
        assert avatar2.position == "right_out"
        assert avatar2.flip == True
        assert avatar2.scale_percent == 75
        
        # クリーンアップ
        avatar1.frame_timer.stop()
        avatar1.follow_timer.stop()
        avatar2.frame_timer.stop()
        avatar2.follow_timer.stop()