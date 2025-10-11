# tests/avatar/test_update_frame.py
import pytest
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QSize
from pvv_mcp_server.avatar.mod_update_frame import update_frame


class TestUpdateFrame:
    """update_frame関数のユニットテスト"""

    def test_update_frame_normal_case(self):
        """正常系: フレーム更新とインデックスのインクリメント"""
        # Arrange
        mock_self = Mock()
        mock_label = Mock(spec=QLabel)
        mock_pixmap1 = Mock(spec=QPixmap)
        mock_pixmap2 = Mock(spec=QPixmap)
        mock_pixmap3 = Mock(spec=QPixmap)
        
        # QPixmapのsizeメソッドをモック
        mock_size = Mock(spec=QSize)
        mock_pixmap1.size.return_value = mock_size
        mock_pixmap2.size.return_value = mock_size
        mock_pixmap3.size.return_value = mock_size
        
        mock_self.label = mock_label
        mock_self.anime_key = "idle"
        mock_self.anime_index = 0
        mock_self.flip = False
        mock_self.pixmap_dict = {
            "idle": {
                False: [mock_pixmap1, mock_pixmap2, mock_pixmap3],
                True: []
            }
        }
        mock_self.resize = Mock()
        
        # Act
        update_frame(mock_self)
        
        # Assert
        mock_label.setPixmap.assert_called_once_with(mock_pixmap1)
        mock_label.resize.assert_called_once_with(mock_size)
        mock_self.resize.assert_called_once_with(mock_size)
        assert mock_self.anime_index == 1

    def test_update_frame_with_flip_true(self):
        """正常系: flip=Trueの場合の動作確認"""
        # Arrange
        mock_self = Mock()
        mock_label = Mock(spec=QLabel)
        mock_pixmap_flipped1 = Mock(spec=QPixmap)
        mock_pixmap_flipped2 = Mock(spec=QPixmap)
        
        mock_size = Mock(spec=QSize)
        mock_pixmap_flipped1.size.return_value = mock_size
        mock_pixmap_flipped2.size.return_value = mock_size
        
        mock_self.label = mock_label
        mock_self.anime_key = "talking"
        mock_self.anime_index = 0
        mock_self.flip = True
        mock_self.pixmap_dict = {
            "talking": {
                False: [],
                True: [mock_pixmap_flipped1, mock_pixmap_flipped2]
            }
        }
        mock_self.resize = Mock()
        
        # Act
        update_frame(mock_self)
        
        # Assert
        mock_label.setPixmap.assert_called_once_with(mock_pixmap_flipped1)
        assert mock_self.anime_index == 1

    def test_update_frame_increment_index(self):
        """正常系: インデックスが途中から進む場合"""
        # Arrange
        mock_self = Mock()
        mock_label = Mock(spec=QLabel)
        mock_pixmap1 = Mock(spec=QPixmap)
        mock_pixmap2 = Mock(spec=QPixmap)
        mock_pixmap3 = Mock(spec=QPixmap)
        
        mock_size = Mock(spec=QSize)
        mock_pixmap2.size.return_value = mock_size
        
        mock_self.label = mock_label
        mock_self.anime_key = "talking"
        mock_self.anime_index = 1
        mock_self.flip = False
        mock_self.pixmap_dict = {
            "talking": {
                False: [mock_pixmap1, mock_pixmap2, mock_pixmap3],
                True: []
            }
        }
        mock_self.resize = Mock()
        
        # Act
        update_frame(mock_self)
        
        # Assert
        mock_label.setPixmap.assert_called_once_with(mock_pixmap2)
        assert mock_self.anime_index == 2

    def test_update_frame_wrap_around(self):
        """正常系: インデックスが画像リストの末尾に達したら0に戻る"""
        # Arrange
        mock_self = Mock()
        mock_label = Mock(spec=QLabel)
        mock_pixmap1 = Mock(spec=QPixmap)
        mock_pixmap2 = Mock(spec=QPixmap)
        mock_pixmap3 = Mock(spec=QPixmap)
        
        mock_size = Mock(spec=QSize)
        mock_pixmap3.size.return_value = mock_size
        
        mock_self.label = mock_label
        mock_self.anime_key = "blink"
        mock_self.anime_index = 2  # 最後のインデックス
        mock_self.flip = False
        mock_self.pixmap_dict = {
            "blink": {
                False: [mock_pixmap1, mock_pixmap2, mock_pixmap3],
                True: []
            }
        }
        mock_self.resize = Mock()
        
        # Act
        update_frame(mock_self)
        
        # Assert
        mock_label.setPixmap.assert_called_once_with(mock_pixmap3)
        assert mock_self.anime_index == 0  # ラップアラウンド

    def test_update_frame_single_image(self):
        """正常系: 画像が1枚しかない場合"""
        # Arrange
        mock_self = Mock()
        mock_label = Mock(spec=QLabel)
        mock_pixmap1 = Mock(spec=QPixmap)
        
        mock_size = Mock(spec=QSize)
        mock_pixmap1.size.return_value = mock_size
        
        mock_self.label = mock_label
        mock_self.anime_key = "static"
        mock_self.anime_index = 0
        mock_self.flip = False
        mock_self.pixmap_dict = {
            "static": {
                False: [mock_pixmap1],
                True: []
            }
        }
        mock_self.resize = Mock()
        
        # Act
        update_frame(mock_self)
        
        # Assert
        mock_label.setPixmap.assert_called_once_with(mock_pixmap1)
        assert mock_self.anime_index == 0  # 1枚なので0に戻る

    def test_update_frame_no_pixmap_dict(self):
        """異常系: pixmap_dictが存在しない場合"""
        # Arrange
        mock_self = Mock(spec=[])  # pixmap_dictを持たない
        
        # Act
        update_frame(mock_self)
        
        # Assert
        # 例外が発生せず、何もしないことを確認
        assert not hasattr(mock_self, 'pixmap_dict')

    def test_update_frame_empty_pixmap_dict(self):
        """異常系: pixmap_dictが空の場合"""
        # Arrange
        mock_self = Mock()
        mock_self.pixmap_dict = {}
        
        # Act
        update_frame(mock_self)
        
        # Assert
        # 例外が発生せず、何もしないことを確認
        assert mock_self.pixmap_dict == {}

    def test_update_frame_anime_key_not_found(self):
        """異常系: anime_keyが存在しない場合"""
        # Arrange
        mock_self = Mock()
        mock_self.pixmap_dict = {
            "idle": {False: [], True: []}
        }
        mock_self.anime_key = "non_existent"
        
        # Act
        update_frame(mock_self)
        
        # Assert
        # 例外が発生せず、何もしないことを確認
        assert mock_self.anime_key == "non_existent"

    def test_update_frame_no_label(self):
        """異常系: labelが存在しない場合"""
        # Arrange
        mock_self = Mock()
        mock_pixmap1 = Mock(spec=QPixmap)
        
        mock_self.anime_key = "idle"
        mock_self.anime_index = 0
        mock_self.flip = False
        mock_self.pixmap_dict = {
            "idle": {
                False: [mock_pixmap1],
                True: []
            }
        }
        # labelを削除
        delattr(mock_self, 'label')
        
        # Act
        update_frame(mock_self)
        
        # Assert
        # 例外が発生せず、何もしないことを確認
        assert not hasattr(mock_self, 'label')

    def test_update_frame_empty_pixmap_list(self):
        """異常系: 画像リストが空の場合"""
        # Arrange
        mock_self = Mock()
        mock_label = Mock(spec=QLabel)
        
        mock_self.label = mock_label
        mock_self.anime_key = "empty"
        mock_self.anime_index = 0
        mock_self.flip = False
        mock_self.pixmap_dict = {
            "empty": {
                False: [],  # 空のリスト
                True: []
            }
        }
        
        # Act
        update_frame(mock_self)
        
        # Assert
        # setPixmapが呼ばれないことを確認
        mock_label.setPixmap.assert_not_called()

    def test_update_frame_no_anime_index(self):
        """正常系: anime_indexが存在しない場合は0で初期化される"""
        # Arrange
        mock_self = Mock()
        mock_label = Mock(spec=QLabel)
        mock_pixmap1 = Mock(spec=QPixmap)
        
        mock_size = Mock(spec=QSize)
        mock_pixmap1.size.return_value = mock_size
        
        mock_self.label = mock_label
        mock_self.anime_key = "idle"
        mock_self.flip = False
        mock_self.pixmap_dict = {
            "idle": {
                False: [mock_pixmap1],
                True: []
            }
        }
        mock_self.resize = Mock()
        # anime_indexを削除
        if hasattr(mock_self, 'anime_index'):
            delattr(mock_self, 'anime_index')
        
        # Act
        update_frame(mock_self)
        
        # Assert
        mock_label.setPixmap.assert_called_once_with(mock_pixmap1)
        assert mock_self.anime_index == 0  # 初期化されて、1枚なので0に戻る
        