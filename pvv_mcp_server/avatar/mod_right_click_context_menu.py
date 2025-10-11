"""
mod_right_click_context_menu.py
右クリックでコンテキストメニューを表示するモジュール
"""

from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import QPoint
import logging
import sys
from functools import partial

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# stderrへの出力ハンドラー
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def right_click_context_menu(self, mouse_position: QPoint) -> None:
    """
    右クリック時にコンテキストメニューを表示する
    
    Args:
        self: AvatarWindowのインスタンス
        position: メニューを表示する位置
    
    Returns:
        None
    """
    # コンテキストメニューを作成
    menu = QMenu(self)
    
    # アニメーション選択サブメニュー
    animation_menu = menu.addMenu("アニメーション")
    
    # pixmap_dictが存在する場合、アニメーションキーをメニューに追加
    if hasattr(self, "pixmap_dict") and self.pixmap_dict:
        for anime_key in self.pixmap_dict.keys():
            action = QAction(anime_key, self)
            action.triggered.connect(lambda checked=False, key=anime_key: self.set_anime_key(key))
            animation_menu.addAction(action)

    else:
        # アニメーションが登録されていない場合
        no_anime_action = QAction("(なし)", self)
        no_anime_action.setEnabled(False)
        animation_menu.addAction(no_anime_action)
    
    menu.addSeparator()

        
    # アニメーション速度設定サブメニュー
    speed_menu = menu.addMenu("アニメーション速度")
    
    speeds = [
        ("超高速 (50ms)", 50),
        ("高速 (100ms)", 100),
        ("通常 (150ms)", 150),
        ("低速 (200ms)", 200),
        ("超低速 (250ms)", 250)
    ]
    
    current_speed = getattr(self, 'frame_timer_interval', 100)
    
    for label, speed_ms in speeds:
        action = QAction(label, self)
        action.setCheckable(True)
        action.setChecked(current_speed == speed_ms)
        action.triggered.connect(lambda checked=False, key=speed_ms: self.set_frame_timer_interval(key))
        speed_menu.addAction(action)
    
    menu.addSeparator()


    # 表示位置選択サブメニュー
    position_menu = menu.addMenu("表示位置")
    
    positions = [
        ("左下外側", "left_out"),
        ("左下内側", "left_in"),
        ("右下内側", "right_in"),
        ("右下外側", "right_out")
    ]
    
    current_position = getattr(self, 'position', 'left_out')
    
    for label, pos_key in positions:
        action = QAction(label, self)
        action.setCheckable(True)
        action.setChecked(current_position == pos_key)
        action.triggered.connect(lambda checked=False, key=pos_key: self.set_position(key))
        position_menu.addAction(action)

    menu.addSeparator()
    
    # 左右反転メニュー
    flip_action = QAction("左右反転", self)
    flip_action.setCheckable(True)
    flip_action.setChecked(self.flip)
    flip_action.triggered.connect(lambda checked: self.set_flip(checked))
    menu.addAction(flip_action)

    menu.addSeparator()

    # 位置追随設定
    follow_menu = menu.addMenu("位置追随")
    
    follow_on_action = QAction("ON", self)
    follow_on_action.setCheckable(True)
    follow_on_action.setChecked(self.follow_timer.isActive())
    follow_on_action.triggered.connect(lambda: self.follow_timer.start())
    follow_menu.addAction(follow_on_action)
    
    follow_off_action = QAction("OFF", self)
    follow_off_action.setCheckable(True)
    follow_off_action.setChecked(not self.follow_timer.isActive())
    follow_off_action.triggered.connect(lambda: self.follow_timer.stop())
    follow_menu.addAction(follow_off_action)
    
    menu.addSeparator()

    
    # 終了アクション
    # exit_action = QAction("終了", self)
    # exit_action.triggered.connect(self.close)
    # menu.addAction(exit_action)
    
    # メニューを表示
    menu.exec(self.mapToGlobal(mouse_position))
