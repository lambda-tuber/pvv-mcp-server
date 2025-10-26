"""
test_avatar_dialog.py
avatar.mod_avatar_dialogモジュールのユニットテスト
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch, call, NonCallableMock
from collections import defaultdict


# PySide6を完全にモック化（インポート前に実行）
mock_qt = MagicMock()
mock_qt.WindowStaysOnTopHint = 1
mock_qt.AlignCenter = 2
mock_qt.transparent = 3
mock_qt.KeepAspectRatio = 4
mock_qt.SmoothTransformation = 5
mock_qt.IgnoreAspectRatio = 6 

class MockQWidget:
    """QWidgetの最低限のモック"""
    def __init__(self, *args, **kwargs):
        # 継承元の__init__が呼ばれた場合を想定し、引数を受け取る
        pass 
        
    def show(self): pass
    def hide(self): pass
    def closeEvent(self, event): pass
    def setWindowTitle(self, title): pass
    def setWindowFlags(self, flags): pass
    
    def __getattr__(self, name):
        # 属性にアクセスされたときにMagicMockを動的に返す
        return MagicMock(name=f"MockQWidget.{name}")

# PySide6モジュールをモック化
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtCore'].Qt = mock_qt
sys.modules['PySide6.QtWidgets'] = MagicMock()
# 💡 修正 2: QDialogのモックをMockQWidgetに変更し、dialog.zip_datがMagicMockになる問題を解消
sys.modules['PySide6.QtWidgets'].QDialog = MockQWidget 
sys.modules['PySide6.QtWidgets'].QLabel = MagicMock(spec=MockQWidget)
sys.modules['PySide6.QtGui'] = MagicMock()


@pytest.fixture
def mock_zip_dat():
    """zipデータのモック"""
    zip_dat = defaultdict(dict)
    # 各パーツカテゴリにダミーファイルを追加
    parts = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
    for part in parts:
        zip_dat[part][f"{part}_01.png"] = b"dummy_png_data_1"
        zip_dat[part][f"{part}_02.png"] = b"dummy_png_data_2"
    return zip_dat


@pytest.fixture
def mock_parent():
    """親ウィジェットのモック"""
    return MagicMock()


@pytest.fixture
def test_config():
    """テスト用設定"""
    return {
        "parts": {
            "顔": {
                "base_image": "顔_01.png",
                "anime_images": ["顔_01.png", "顔_02.png"],
                "current_index": 0
            },
            "目": {
                "base_image": "目_01.png",
                "anime_images": ["目_01.png"],
                "current_index": 0
            }
        }
    }


def create_avatar_part_widget_side_effect(*args, **kwargs):
    """
    AvatarPartWidget.__init__が呼び出されたときに実行される関数。
    インスタンス化の際に渡されたカテゴリ名に基づいてモックのupdate()の戻り値を設定する。
    """
    # 最初の引数（args[0]）がカテゴリ名（'後', '体'など）であると仮定
    part_category = args[0] if args else "後"
    
    mock = MagicMock()
    mock.save_config.return_value = {
        "base_image": f"{part_category}_01.png",
        "anime_images": [f"{part_category}_01.png", f"{part_category}_02.png"],
        "current_index": 0
    }
    mock.load_config.return_value = None
    mock.start_oneshot.return_value = None
    
    # 💡 修正 3: update()は、そのカテゴリの最初のファイル名（文字列）を返す
    mock.update.return_value = f"{part_category}_01.png"
    
    return mock


class TestAvatarDialogInit:
    """__init__メソッドのテスト"""
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_init_without_config(self, mock_widget_class, mock_parent, mock_zip_dat):
        """設定なしでの初期化"""
        # 💡 修正 1: side_effectに関数を設定し、呼び出しごとに新しいモックを生成
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        # 基本属性が設定されていることを確認
        assert dialog.zip_dat == mock_zip_dat
        assert dialog.scale == 50
        assert dialog.flip == False
        assert dialog.current_pixmap is None
        
        # 8つのパーツウィジェットが作成されたことを確認
        assert len(dialog.part_widgets) == 8
        assert mock_widget_class.call_count == 8
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_init_with_config(self, mock_widget_class, mock_parent, mock_zip_dat, test_config):
        """設定ありでの初期化"""
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 75, True, 50, test_config)
        
        # 基本属性が設定されていることを確認
        assert dialog.scale == 75
        assert dialog.flip == True


class TestAvatarDialogGUI:
    """GUIセットアップのテスト"""
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_setup_gui(self, mock_widget_class, mock_parent, mock_zip_dat):
        """GUIセットアップ"""
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        # center_labelが作成されたことを確認
        assert hasattr(dialog, 'center_label')
        assert dialog.center_label is not None


class TestAvatarDialogCloseEvent:
    """closeEventのテスト"""
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_close_event_hide_instead_close(self, mock_widget_class, mock_parent, mock_zip_dat):
        """×ボタンクリック時にhideが呼ばれる"""
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        # イベントのモック
        mock_event = MagicMock()
        
        # closeEventを呼び出し
        dialog.closeEvent(mock_event)
        
        # イベントが無視されることを確認
        mock_event.ignore.assert_called_once()


class TestAvatarDialogConfig:
    """save_config/load_configのテスト"""
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_save_config(self, mock_widget_class, mock_parent, mock_zip_dat):
        """設定の保存"""
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        config = dialog.save_config()
        
        # 設定辞書の構造を確認
        assert "parts" in config
        assert len(config["parts"]) == 8
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_load_config(self, mock_widget_class, mock_parent, mock_zip_dat, test_config):
        """設定の読み込み"""
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        dialog.load_config(test_config)
        
        # 例外が発生しないことを確認（load_configの呼び出しが成功した）
        assert True
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_load_config_unknown_part(self, mock_widget_class, mock_parent, mock_zip_dat):
        """未知のパーツ名を含む設定の読み込み"""
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        # 未知のパーツ名を含む設定
        invalid_config = {
            "parts": {
                "未知パーツ": {"base_image": "test.png"}
            }
        }
        
        # 例外が発生しないことを確認
        dialog.load_config(invalid_config)


class TestAvatarDialogSetters:
    """setter系メソッドのテスト"""
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_set_flip(self, mock_widget_class, mock_parent, mock_zip_dat):
        """左右反転の設定"""
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        # 初期値を確認
        assert dialog.flip == False
        
        # 反転を有効化
        dialog.set_flip(True)
        assert dialog.flip == True
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_set_scale(self, mock_widget_class, mock_parent, mock_zip_dat):
        """スケールの設定"""
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        # 初期値を確認
        assert dialog.scale == 50
        
        # スケールを変更
        dialog.set_scale(75)
        assert dialog.scale == 75


class TestAvatarDialogPublicFunctions:
    """public関数のテスト"""
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_get_current_pixmap(self, mock_widget_class, mock_parent, mock_zip_dat):
        """現在のPixmapの取得"""
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        # 初期状態ではNone
        assert dialog.get_current_pixmap() is None
        
        # current_pixmapを設定
        mock_pixmap = MagicMock()
        dialog.current_pixmap = mock_pixmap
        
        # 設定したPixmapが取得できることを確認
        assert dialog.get_current_pixmap() == mock_pixmap
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_start_oneshot(self, mock_widget_class, mock_parent, mock_zip_dat):
        """ワンショットアニメーションの開始"""
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        dialog.start_oneshot()
        
        # 例外が発生しないことを確認
        assert True


class TestAvatarDialogUpdateFrame:
    """update_frameメソッドのテスト"""
    
    @patch('pvv_mcp_server.avatar.mod_avatar_dialog.QImage')
    @patch('pvv_mcp_server.avatar.mod_avatar_dialog.QPainter')
    @patch('pvv_mcp_server.avatar.mod_avatar_dialog.QPixmap')
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_update_frame_with_parts(self, mock_widget_class, mock_qpixmap, 
                                     mock_qpainter, mock_qimage,
                                     mock_parent, mock_zip_dat):
        """パーツありでのフレーム更新"""
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        # QImageのモック
        mock_image_instance = MagicMock()
        mock_image_instance.width.return_value = 400
        mock_image_instance.height.return_value = 400
        mock_qimage.return_value = mock_image_instance
        
        # QPixmapのモック
        mock_pixmap_instance = MagicMock()
        mock_pixmap_instance.width.return_value = 400
        mock_pixmap_instance.height.return_value = 400
        mock_pixmap_instance.scaled.return_value = mock_pixmap_instance
        mock_qpixmap.fromImage.return_value = mock_pixmap_instance
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        dialog.update_frame()
        
        # 例外が発生しないことを確認
        assert True
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_update_frame_no_parts(self, mock_widget_class, mock_parent, mock_zip_dat):
        """パーツなしでのフレーム更新"""
        
        # パーツウィジェットがNoneを返すモックを作成する関数
        def create_none_mock(*args, **kwargs):
            mock_widget = MagicMock()
            mock_widget.update.return_value = None
            mock_widget.save_config.return_value = {}
            mock_widget.load_config.return_value = None
            mock_widget.start_oneshot.return_value = None
            return mock_widget
        
        # side_effectに関数を設定
        mock_widget_class.side_effect = create_none_mock
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        # 例外が発生しないことを確認
        dialog.update_frame()
        
        # current_pixmapがNoneのままであることを確認
        assert dialog.current_pixmap is None


class TestAvatarDialogIntegration:
    """統合テスト"""
    
    @patch('pvv_mcp_server.avatar.mod_avatar_part.AvatarPartWidget')
    def test_full_workflow(self, mock_widget_class, mock_parent, mock_zip_dat, test_config):
        """初期化→設定保存→設定読み込みの一連の流れ"""
        mock_widget_class.side_effect = create_avatar_part_widget_side_effect
        
        from pvv_mcp_server.avatar.mod_avatar_dialog import AvatarDialog
        # ダイアログ作成
        dialog = AvatarDialog(mock_parent, mock_zip_dat, 50, False, 100, None)
        
        # 設定の保存
        saved_config = dialog.save_config()
        assert "parts" in saved_config
        
        # 設定の読み込み
        dialog.load_config(test_config)
        
        # スケールと反転の設定変更
        dialog.set_scale(75)
        dialog.set_flip(True)
        
        assert dialog.scale == 75
        assert dialog.flip == True
        
        # ワンショット開始
        dialog.start_oneshot()
        
        # 統合テストが正常に完了したことを確認
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])