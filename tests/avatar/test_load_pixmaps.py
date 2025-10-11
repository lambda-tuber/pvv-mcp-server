"""
test_load_pixmaps.py
mod_load_pixmaps.pyのユニットテスト
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap

# テスト対象のモジュールをインポート
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pvv_mcp_server', 'avatar'))
from pvv_mcp_server.avatar.mod_load_pixmaps import load_pixmaps


@pytest.fixture(scope='module')
def qapp():
    """QApplicationのフィクスチャ（QPixmap使用に必要）"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_self():
    """モックのselfオブジェクト"""
    return Mock()


@pytest.fixture
def temp_image_files(tmp_path):
    """テスト用の一時画像ファイルを作成"""
    # 簡単なPNG画像を作成
    pixmap = QPixmap(100, 100)
    pixmap.fill()
    
    image_paths = []
    for i in range(3):
        image_path = tmp_path / f"test_image_{i}.png"
        pixmap.save(str(image_path))
        image_paths.append(str(image_path))
    
    return image_paths


class TestLoadPixmaps:
    """load_pixmaps関数のテストクラス"""
    
    def test_basic_loading(self, qapp, mock_self, temp_image_files):
        """基本的な画像読み込みのテスト"""
        image_dict = {
            "idle": temp_image_files
        }
        
        result = load_pixmaps(mock_self, image_dict)
        
        # 結果の構造を確認
        assert "idle" in result
        assert False in result["idle"]
        assert True in result["idle"]
        
        # 画像リストの長さを確認
        assert len(result["idle"][False]) == 3
        assert len(result["idle"][True]) == 3
        
        # QPixmapオブジェクトであることを確認
        for pixmap in result["idle"][False]:
            assert isinstance(pixmap, QPixmap)
            assert not pixmap.isNull()
        
        for pixmap in result["idle"][True]:
            assert isinstance(pixmap, QPixmap)
            assert not pixmap.isNull()
    
    def test_multiple_anime_keys(self, qapp, mock_self, temp_image_files):
        """複数のアニメーションキーのテスト"""
        image_dict = {
            "idle": [temp_image_files[0]],
            "talk": [temp_image_files[1], temp_image_files[2]]
        }
        
        result = load_pixmaps(mock_self, image_dict)
        
        # 両方のキーが存在することを確認
        assert "idle" in result
        assert "talk" in result
        
        # それぞれのキーにFalse/Trueが存在することを確認
        assert len(result["idle"][False]) == 1
        assert len(result["idle"][True]) == 1
        assert len(result["talk"][False]) == 2
        assert len(result["talk"][True]) == 2
    
    def test_scaling(self, qapp, mock_self, temp_image_files):
        """スケーリングのテスト"""
        image_dict = {
            "idle": [temp_image_files[0]]
        }
        
        result = load_pixmaps(mock_self, image_dict, scale_percent=50)
        
        # スケーリングされた画像サイズを確認
        original_pixmap = QPixmap(temp_image_files[0])
        scaled_pixmap = result["idle"][False][0]
        
        assert scaled_pixmap.width() == original_pixmap.width() // 2
        assert scaled_pixmap.height() == original_pixmap.height() // 2
    
    def test_flip_difference(self, qapp, mock_self, temp_image_files):
        """反転画像が元画像と異なることを確認"""
        image_dict = {
            "idle": [temp_image_files[0]]
        }
        
        result = load_pixmaps(mock_self, image_dict)
        
        original = result["idle"][False][0]
        flipped = result["idle"][True][0]
        
        # サイズは同じであることを確認
        assert original.width() == flipped.width()
        assert original.height() == flipped.height()
        
        # 画像が異なることを確認（QImageに変換して比較）
        original_image = original.toImage()
        flipped_image = flipped.toImage()
        
        # 左端と右端のピクセルが入れ替わっていることを確認
        assert original_image.pixel(0, 0) == flipped_image.pixel(flipped_image.width() - 1, 0)
    
    def test_nonexistent_file(self, qapp, mock_self):
        """存在しないファイルの処理テスト"""
        image_dict = {
            "idle": ["nonexistent_file.png"]
        }
        
        result = load_pixmaps(mock_self, image_dict)
        
        # 存在しないファイルはスキップされる
        assert "idle" in result
        assert len(result["idle"][False]) == 0
        assert len(result["idle"][True]) == 0
    
    def test_empty_image_dict(self, qapp, mock_self):
        """空の辞書の処理テスト"""
        image_dict = {}
        
        result = load_pixmaps(mock_self, image_dict)
        
        assert result == {}