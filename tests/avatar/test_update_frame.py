"""
test_update_frame.py
mod_update_frameのユニットテスト
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pvv_mcp_server.avatar.mod_update_frame import update_frame


class TestUpdateFrame:
    """update_frame関数のテストクラス"""
    
    @pytest.fixture
    def mock_pixmap(self):
        """QPixmapのモックを作成"""
        pixmap = Mock()
        pixmap.width.return_value = 300
        pixmap.height.return_value = 500
        return pixmap
    
    @pytest.fixture
    def mock_dialog(self, mock_pixmap):
        """Dialogのモックを作成"""
        dialog = Mock()
        dialog.update_frame = Mock()
        dialog.get_current_pixmap = Mock(return_value=mock_pixmap)
        return dialog
    
    @pytest.fixture
    def mock_avatar(self, mock_dialog):
        """AvatarWindowのモックを作成"""
        avatar = Mock()
        avatar.zip_data = b"dummy_zip_data"  # zipデータが存在する状態
        avatar.anime_type = "idle"
        avatar.dialogs = {"idle": mock_dialog}
        
        # QLabel のモック
        avatar.label = Mock()
        avatar.label.setPixmap = Mock()
        avatar.label.adjustSize = Mock()
        avatar.adjustSize = Mock()
        
        return avatar
    
    def test_update_frame_success(self, mock_avatar, mock_dialog, mock_pixmap):
        """正常にフレームが更新される場合のテスト"""
        update_frame(mock_avatar)
        
        # dialogのupdate_frameが呼ばれることを確認
        mock_dialog.update_frame.assert_called_once()
        
        # dialogからpixmapを取得することを確認
        mock_dialog.get_current_pixmap.assert_called_once()
        
        # labelにpixmapが設定されることを確認
        mock_avatar.label.setPixmap.assert_called_once_with(mock_pixmap)
        
        # サイズ調整が呼ばれることを確認
        mock_avatar.label.adjustSize.assert_called_once()
        mock_avatar.adjustSize.assert_called_once()
    
    def test_update_frame_no_zip_data(self, mock_avatar):
        """zip_dataが存在しない場合のテスト"""
        mock_avatar.zip_data = None
        
        update_frame(mock_avatar)
        
        # 何も処理されないことを確認
        assert not mock_avatar.label.setPixmap.called
    
    def test_update_frame_no_dialog(self, mock_avatar):
        """該当するdialogが存在しない場合のテスト"""
        mock_avatar.anime_type = "non_existent"
        
        update_frame(mock_avatar)
        
        # 何も処理されないことを確認
        assert not mock_avatar.label.setPixmap.called
    
    def test_update_frame_dialog_none(self, mock_avatar):
        """dialogsにNoneが入っている場合のテスト"""
        mock_avatar.dialogs = {"idle": None}
        
        update_frame(mock_avatar)
        
        # 何も処理されないことを確認
        assert not mock_avatar.label.setPixmap.called
    
    def test_update_frame_pixmap_none(self, mock_avatar, mock_dialog):
        """get_current_pixmapがNoneを返す場合のテスト"""
        mock_dialog.get_current_pixmap.return_value = None
        
        update_frame(mock_avatar)
        
        # update_frameは呼ばれる
        mock_dialog.update_frame.assert_called_once()
        
        # しかしsetPixmapは呼ばれない
        assert not mock_avatar.label.setPixmap.called
    
    def test_update_frame_exception_in_dialog_update(self, mock_avatar, mock_dialog):
        """dialog.update_frame()で例外が発生する場合のテスト"""
        mock_dialog.update_frame.side_effect = Exception("Test exception")
        
        # 例外が外部に漏れないことを確認
        update_frame(mock_avatar)
        
        # setPixmapは呼ばれない
        assert not mock_avatar.label.setPixmap.called
    
    def test_update_frame_exception_in_get_pixmap(self, mock_avatar, mock_dialog):
        """dialog.get_current_pixmap()で例外が発生する場合のテスト"""
        mock_dialog.get_current_pixmap.side_effect = Exception("Test exception")
        
        # 例外が外部に漏れないことを確認
        update_frame(mock_avatar)
        
        # setPixmapは呼ばれない
        assert not mock_avatar.label.setPixmap.called
    
    def test_update_frame_exception_in_set_pixmap(self, mock_avatar, mock_dialog, mock_pixmap):
        """label.setPixmap()で例外が発生する場合のテスト"""
        mock_avatar.label.setPixmap.side_effect = Exception("Test exception")
        
        # 例外が外部に漏れないことを確認
        update_frame(mock_avatar)
        
        # update_frameとget_current_pixmapは呼ばれる
        mock_dialog.update_frame.assert_called_once()
        mock_dialog.get_current_pixmap.assert_called_once()
    
    def test_update_frame_multiple_anime_types(self, mock_avatar, mock_pixmap):
        """複数のアニメタイプが存在する場合のテスト"""
        # 複数のdialogを設定
        mock_dialog_idle = Mock()
        mock_dialog_idle.update_frame = Mock()
        mock_dialog_idle.get_current_pixmap = Mock(return_value=mock_pixmap)
        
        mock_dialog_talk = Mock()
        mock_dialog_talk.update_frame = Mock()
        mock_dialog_talk.get_current_pixmap = Mock(return_value=mock_pixmap)
        
        mock_avatar.dialogs = {
            "idle": mock_dialog_idle,
            "talk": mock_dialog_talk
        }
        mock_avatar.anime_type = "talk"
        
        update_frame(mock_avatar)
        
        # talkのdialogだけが呼ばれることを確認
        assert not mock_dialog_idle.update_frame.called
        mock_dialog_talk.update_frame.assert_called_once()
        mock_dialog_talk.get_current_pixmap.assert_called_once()
        
        # labelに設定される
        mock_avatar.label.setPixmap.assert_called_once_with(mock_pixmap)
    
    def test_update_frame_empty_dialogs(self, mock_avatar):
        """dialogsが空の辞書の場合のテスト"""
        mock_avatar.dialogs = {}
        
        update_frame(mock_avatar)
        
        # 何も処理されない
        assert not mock_avatar.label.setPixmap.called
    
    def test_update_frame_adjust_size_called_in_order(self, mock_avatar, mock_dialog, mock_pixmap):
        """adjustSizeが正しい順序で呼ばれることを確認"""
        call_order = []
        
        mock_avatar.label.setPixmap.side_effect = lambda p: call_order.append('setPixmap')
        mock_avatar.label.adjustSize.side_effect = lambda: call_order.append('label.adjustSize')
        mock_avatar.adjustSize.side_effect = lambda: call_order.append('avatar.adjustSize')
        
        update_frame(mock_avatar)
        
        # 呼び出し順序を確認
        assert call_order == ['setPixmap', 'label.adjustSize', 'avatar.adjustSize']
    
    def test_update_frame_with_different_pixmap_sizes(self, mock_avatar, mock_dialog):
        """異なるサイズのpixmapでも正常に動作することをテスト"""
        pixmaps = [
            Mock(width=Mock(return_value=100), height=Mock(return_value=100)),
            Mock(width=Mock(return_value=500), height=Mock(return_value=1000)),
            Mock(width=Mock(return_value=1920), height=Mock(return_value=1080))
        ]
        
        for pixmap in pixmaps:
            mock_dialog.get_current_pixmap.return_value = pixmap
            update_frame(mock_avatar)
            mock_avatar.label.setPixmap.assert_called_with(pixmap)
