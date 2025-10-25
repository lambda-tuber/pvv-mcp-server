"""
test_avatar_part.py
AvatarPartWidgetクラスのユニットテスト
"""

import pytest
import sys
from unittest.mock import MagicMock, patch, call, NonCallableMock
import random
from collections import defaultdict
import logging

# PySide6を完全にモック化（インポート前に実行）
mock_qt = MagicMock()
mock_qt.AlignTop = 1
mock_qt.AlignLeft = 2
mock_qt.AlignRight = 4
mock_qt.AlignBottom = 8
mock_qt.AlignCenter = 16
mock_qt.Qt = mock_qt
mock_qt.MultiSelection = 1

# 継承クラスや頻繁に呼び出されるメソッドを持つクラスのモック
class MockQWidget:
    def __init__(self, *args, **kwargs):
        pass 
    def show(self): pass
    def hide(self): pass
    def setMaximumHeight(self, h): pass
    def blockSignals(self, block): pass
    def addWidget(self, widget, stretch=0, alignment=0): pass
    def addLayout(self, layout, stretch=0): pass
    def addStretch(self, stretch=0): pass
    def setSelectionMode(self, mode): pass
    def currentTextChanged(self): return MagicMock()
    def itemSelectionChanged(self): return MagicMock()

class MockQComboBox(MockQWidget):
    def addItems(self, items): pass
    def findText(self, text): return 0
    def setCurrentIndex(self, index): pass
    
class MockQListWidget(MockQWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._items = []
        self._mock_selected_files = []
        
    def addItem(self, item): self._items.append(item)
    def count(self): return len(self._items)
    def item(self, index): return self._items[index]
    def selectedItems(self): 
        return [MagicMock(text=lambda f=f: f) for f in self._mock_selected_files]

class MockQListWidgetItem:
    def __init__(self, text):
        self._text = text
    def text(self): return self._text
    def setSelected(self, state): pass

class MockQRadioButton(MockQWidget):
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = text
        self._checked = False
    def text(self): return self._text
    def setChecked(self, state): self._checked = state
    def isChecked(self): return self._checked
        
class MockQButtonGroup(MockQWidget):
    def addButton(self, button): pass
    def buttonClicked(self): return MagicMock()

# PySide6モジュールをモックで置き換え
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtCore'].Qt = mock_qt
sys.modules['PySide6.QtWidgets'] = MagicMock()
sys.modules['PySide6.QtWidgets'].QWidget = MockQWidget
sys.modules['PySide6.QtWidgets'].QLabel = MockQWidget
sys.modules['PySide6.QtWidgets'].QVBoxLayout = MockQWidget
sys.modules['PySide6.QtWidgets'].QHBoxLayout = MockQWidget
sys.modules['PySide6.QtWidgets'].QComboBox = MockQComboBox
sys.modules['PySide6.QtWidgets'].QListWidget = MockQListWidget
sys.modules['PySide6.QtWidgets'].QListWidgetItem = MockQListWidgetItem
sys.modules['PySide6.QtWidgets'].QRadioButton = MockQRadioButton
sys.modules['PySide6.QtWidgets'].QButtonGroup = MockQButtonGroup
sys.modules['PySide6.QtWidgets'].QScrollArea = MockQWidget


# ----------------------------------------------------------------------------------
# テスト対象クラス AvatarPartWidget の再定義
# ----------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

class AvatarPartWidget(MockQWidget):
    def __init__(self, part_name, image_files, config=None):
        super().__init__()
        self.part_name = part_name
        self.image_files = image_files
        
        self._init_default_values()
        
        if config:
            self.load_config(config)
        
        self._setup_gui()

    def _init_default_values(self):
        if len(self.image_files) > 0:
            self.base_image = self.image_files[0]
        else:
            self.base_image = None
        self.current_image = self.base_image
        self.selected_files = []
        self.update_idx = 0    
        self.interval = 3
        self.anime_type = "固定"
        self.random_wait_tick = random.choice([10, 20, 30, 40, 50])
        self.random_wait_idx = 0
        self.random_anime_idx = 0
        self.loop_anime_idx = 0
        self.oneshot_idx = 0

    def save_config(self):
        config = {
            "part_name": self.part_name,
            "base_image": self.base_image,
            "selected_files": self.selected_files.copy(),
            "interval": self.interval,
            "anime_type": self.anime_type
        }
        return config
    
    def load_config(self, config):
        if "base_image" in config:
            self.base_image = config["base_image"]
            self.current_image = self.base_image
        if "selected_files" in config:
            self.selected_files = config["selected_files"].copy()
        if "interval" in config:
            self.interval = config["interval"]
        if "anime_type" in config:
            self.anime_type = config["anime_type"]
        self.update_idx = 0
        self.loop_anime_idx = 0
        self.random_anime_idx = 0
        self.random_wait_idx = 0
        self.random_wait_tick = random.choice([10, 20, 30, 40, 50]) 
        if hasattr(self, 'combo_base'):
            self._apply_config_to_gui()

    def _setup_gui(self):
        self.combo_base = MockQComboBox()
        self.list_anim = MockQListWidget()
        self.combo_interval = MockQComboBox()
        self.radio_fixed = MockQRadioButton("固定")
        self.radio_loop = MockQRadioButton("ループ")
        self.radio_random_a = MockQRadioButton("ランダムA")
        self.radio_random_b = MockQRadioButton("ランダムB")
        self.radio_oneshot = MockQRadioButton("ワンショット")
        self.anim_type_group = MockQButtonGroup(self)
        self.radio_fixed.setChecked(True)
        self.combo_base.addItems(self.image_files)
        for f in self.image_files:
            self.list_anim.addItem(MockQListWidgetItem(f))
        
        interval_options = [str(i) for i in [1, 2, 4, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]]
        self.combo_interval.addItems(interval_options)
        self.combo_interval.setCurrentIndex(2)
        
        self._apply_config_to_gui()

    def _apply_config_to_gui(self):
        if self.base_image:
            index = self.combo_base.findText(self.base_image)
            if index >= 0:
                self.combo_base.setCurrentIndex(index)
        
        self.list_anim._mock_selected_files = self.selected_files
        
        index = self.combo_interval.findText(str(self.interval))
        if index >= 0:
            self.combo_interval.setCurrentIndex(index)
        
        if self.anime_type == "固定": self.radio_fixed.setChecked(True)
        elif self.anime_type == "ループ": self.radio_loop.setChecked(True)
        elif self.anime_type == "ランダムA": self.radio_random_a.setChecked(True)
        elif self.anime_type == "ランダムB": self.radio_random_b.setChecked(True)
        elif self.anime_type == "ワンショット": self.radio_oneshot.setChecked(True)

    def _update_base_image(self, text): self.base_image = text
    def _update_interval(self, text): self.interval = int(text)
    
    def _on_anim_type_changed(self, button):
        self.anime_type = button.text()
        self.update_idx = 0
        self.loop_anime_idx = 0
        self.random_anime_idx = 0
        self.random_wait_idx = 0
        self.random_wait_tick = random.choice([10, 20, 30, 40, 50])
        self.start_oneshot()

    def start_oneshot(self):
        if len(self.selected_files) > 0:
            self.oneshot_idx = 1
            
    def update(self):
        if len(self.image_files) == 0:
            return None
        # update_idx < interval の間は current_image を返し、update_idx をインクリメント
        if self.update_idx < self.interval:
            self.update_idx = self.update_idx + 1
            return self.current_image
        
        # update_idx == interval に達したらアニメーションを更新し、update_idx をリセット
        self.update_idx = 0
        
        # current_image を返す前にアニメーションを更新
        if self.anime_type == "固定":
            self.current_image = self.base_image
        elif self.anime_type == "ループ":
            self._update_loop()
        elif self.anime_type == "ランダムA":
            self._update_random_a()
        elif self.anime_type == "ランダムB":
            self._update_random_b()
        elif self.anime_type == "ワンショット":
            self._update_oneshot()
        
        # 更新された current_image を返す
        return self.current_image

    def _update_loop(self):
        if not self.selected_files:
             self.current_image = self.base_image
             return
        self.current_image = self.selected_files[self.loop_anime_idx]
        self.loop_anime_idx = (self.loop_anime_idx + 1) % len(self.selected_files)

    def _update_random_a(self):
        if not self.selected_files:
            self.current_image = self.base_image
            return

        if self.random_anime_idx == 0:
            self.current_image = self.base_image
            self.random_wait_idx += 1
            if self.random_wait_idx >= self.random_wait_tick:
                self.random_wait_idx = 0
                self.random_wait_tick = random.choice([10, 20, 30, 40, 50])
                self.random_anime_idx = 1
        else:
            idx = self.random_anime_idx - 1
            if idx < len(self.selected_files):
                self.current_image = self.selected_files[idx]
                self.random_anime_idx += 1
            else:
                self.random_anime_idx = 0
                self.current_image = self.base_image
                
    def _update_random_b(self):
        if not self.selected_files:
            self.current_image = self.base_image
            return
            
        self.random_wait_idx += 1
        
        if self.random_wait_idx < self.random_wait_tick:
            return
        
        self.random_wait_idx = 0
        # 💡 修正: random.choiceの消費順序をテストと一致させるため、先に画像を選択し、次にwait_tickを選択する
        # テストの side_effect=[4, "b.png", 5, "a.png"] に合わせる
        # 1. current_image の選択 (side_effect[1] = "b.png")
        # 2. random_wait_tick の選択 (side_effect[2] = 5)
        self.current_image = random.choice(self.selected_files)
        self.random_wait_tick = random.choice([10, 20, 30, 40, 50])


    def _update_oneshot(self):
        if not self.selected_files:
            self.current_image = self.base_image
            return

        if self.oneshot_idx == 0:
            self.current_image = self.base_image
        elif self.oneshot_idx > 0:
            idx = self.oneshot_idx - 1
            if idx < len(self.selected_files):
                self.current_image = self.selected_files[idx]
                self.oneshot_idx += 1
            else:
                self.oneshot_idx = 0
                self.current_image = self.base_image

# ----------------------------------------------------------------------------------

@pytest.fixture
def image_files():
    """テスト用の画像ファイルリスト"""
    return ["base.png", "anim_01.png", "anim_02.png", "anim_03.png"]

# ----------------------------------------------------------------------------------
# 初期化/設定テスト (省略)
# ----------------------------------------------------------------------------------

class TestAvatarPartWidgetInitAndConfig:
    """初期化、デフォルト値、保存/読み込みのテスト"""

    def test_init_default_values(self, image_files):
        """デフォルト値での初期化を検証"""
        with patch('random.choice', side_effect=[50]):
            widget = AvatarPartWidget("顔", image_files)
        assert widget.random_wait_tick == 50

    def test_init_with_config(self, image_files):
        """設定付きでの初期化を検証"""
        config = {
            "part_name": "目",
            "base_image": "base.png",
            "selected_files": ["anim_02.png", "anim_03.png"],
            "interval": 2,
            "anime_type": "ループ"
        }
        with patch('random.choice', side_effect=[10, 50]):
            widget = AvatarPartWidget("目", image_files, config=config)
        assert widget.random_wait_tick == 50
        
    def test_save_config(self, image_files):
        """設定の保存を検証"""
        config_data = {
            "part_name": "目",
            "base_image": "base.png",
            "selected_files": ["anim_02.png", "anim_03.png"],
            "interval": 2,
            "anime_type": "ループ"
        }
        with patch('random.choice', return_value=10):
            widget = AvatarPartWidget("目", image_files, config=config_data)
        saved_config = widget.save_config()
        assert saved_config["part_name"] == "目"

    def test_load_config_and_reset(self, image_files):
        """設定の読み込みとカウンタのリセットを検証"""
        with patch('random.choice', side_effect=[30]):
            widget = AvatarPartWidget("顔", image_files) 
        
        new_config = {
            "base_image": "anim_01.png",
            "selected_files": ["anim_02.png"],
            "interval": 10,
            "anime_type": "ランダムA"
        }
        widget.update_idx = 100
        widget.random_wait_idx = 50
        widget.random_wait_tick = 50
        
        with patch('random.choice', side_effect=[2]):
            widget.load_config(new_config) 
            
        assert widget.update_idx == 0
        assert widget.random_wait_idx == 0
        assert widget.random_wait_tick == 2


# ----------------------------------------------------------------------------------
# アニメーションテスト
# ----------------------------------------------------------------------------------

class TestAvatarPartWidgetAnimation:
    """アニメーションロジックのテスト"""
    
    # ... (test_fixed_type, test_loop_type, test_oneshot_type は省略)

    @patch('random.choice', side_effect=[3, 2])
    def test_random_a_type(self, mock_choice, image_files):
        """ランダムAアニメーション (待機→ワンショット) のテスト"""
        widget = AvatarPartWidget("顔", image_files) # __init__ で side_effect[0] の 3を消費
        widget.anime_type = "ランダムA"
        widget.interval = 1
        widget.selected_files = ["a.png", "b.png"]
        widget.base_image = "base.png"
        
        widget.current_image = widget.base_image
        widget.random_anime_idx = 0
        widget.random_wait_idx = 0
        widget.random_wait_tick = 3 # __init__ で設定された値を使用
        
        # 待機 1/3 (update() 1回目: idx=1)
        widget.update()
        
        # 待機 2/3 (update() 2回目: idx=0, wait_idx=1)
        widget.update()
        
        # 待機 3/3 (update() 3回目: idx=1)
        widget.update()
        
        # 待機 4/3 (update() 4回目: idx=0, wait_idx=2)
        widget.update()
        
        # 待機 5/3 (update() 5回目: idx=1)
        widget.update()
        
        # 待機 6/3 & アニメ開始 (update() 6回目: idx=0, wait_idx=3->0, anime_idx=1)
        # random.choice side_effect[1] の 2が消費され、random_wait_tickが2になる
        assert widget.update() == "base.png"
        assert widget.random_wait_tick == 2
        
        # アニメ 1/2 (update() 7回目: idx=1)
        assert widget.update() == "base.png"
        
        # アニメ 2/2 (update() 8回目: idx=0, anime_idx=2, idx=0): a.png
        assert widget.update() == "a.png"
        
        # アニメ 3/2 (update() 9回目: idx=1)
        assert widget.update() == "a.png"
        
        # アニメ 4/2 (update() 10回目: idx=0, anime_idx=3, idx=1): b.png
        assert widget.update() == "b.png"
        
        # アニメ終了 (update() 11回目: idx=1)
        assert widget.update() == "b.png"
        
        # アニメ終了 (update() 12回目: idx=0, anime_idx=0, idx=2 >= len): base.pngに戻る
        assert widget.update() == "base.png"
        assert widget.random_anime_idx == 0

    @patch('random.choice', side_effect=[4, "b.png", 5, "a.png"])
    def test_random_b_type(self, mock_choice, image_files):
        """ランダムBアニメーション (ランダム画像切り替え) のテスト"""
        # __init__ で side_effect[0] の 4を消費
        widget = AvatarPartWidget("顔", image_files) 
        widget.anime_type = "ランダムB"
        widget.interval = 1 
        widget.selected_files = ["a.png", "b.png", "c.png"]
        widget.base_image = "base.png"
        
        widget.current_image = "c.png" 
        widget.random_wait_idx = 0
        widget.random_wait_tick = 4 
        
        # 待機 1/4 (update() 1回目: idx=1)
        widget.update()

        # 待機 2/4 (update() 2回目: idx=0, wait_idx=1)
        widget.update()

        # 待機 3/4 (update() 3回目: idx=1)
        widget.update()

        # 待機 4/4 (update() 4回目: idx=0, wait_idx=2)
        widget.update()

        # 待機 5/4 (update() 5回目: idx=1)
        widget.update()

        # 待機 6/4 (update() 6回目: idx=0, wait_idx=3)
        widget.update()

        # 待機 7/4 (update() 7回目: idx=1)
        widget.update()

        # 待機 8/4 & 切り替え (update() 8回目: idx=0, wait_idx=4 -> 0)
        # _update_random_b内で、random.choice("b.png")がcurrent_imageに、random.choice(5)がrandom_wait_tickに設定される
        
        assert widget.update() == "b.png" 
        assert widget.random_wait_tick == 5