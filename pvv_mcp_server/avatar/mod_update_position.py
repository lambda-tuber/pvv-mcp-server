"""
mod_update_position.py
アバターウィンドウの位置を更新するモジュール
"""

import pygetwindow as gw
import logging
import sys

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


def update_position(self) -> None:
    """
    self.app_titleで指定されたアプリケーションウィンドウの指定位置に
    下揃えするように、self(AvatarWindow)を移動する
    
    Args:
        self: AvatarWindowのインスタンス
              - self.app_title: ターゲットアプリケーションのウィンドウタイトル
              - self.position: 表示位置 ("left_out", "left_in", "right_in", "right_out")
    
    Returns:
        None
    """
    # app_titleが存在しない場合は何もしない
    if not hasattr(self, 'app_title') or not self.app_title:
        logger.warning("app_title is not set")
        return
    
    # positionが存在しない場合はデフォルト値を設定
    if not hasattr(self, 'position'):
        self.position = "left_out"
    
    try:
        # ターゲットウィンドウを検索
        windows = gw.getWindowsWithTitle(self.app_title)
        
        if not windows:
            logger.warning(f"Window with title '{self.app_title}' not found")
            return
        
        # 最初に見つかったウィンドウを使用
        target_window = windows[0]
        
        # ターゲットウィンドウの位置とサイズを取得
        target_x = target_window.left
        target_y = target_window.top
        target_width = target_window.width
        target_height = target_window.height
        
        # 自身のウィンドウサイズを取得
        avatar_width = self.width()
        avatar_height = self.height()
        
        # positionに応じて配置位置を計算
        if self.position == "left_out":
            # 左下外側（ターゲットウィンドウの左外側）
            new_x = target_x - avatar_width
            new_y = target_y + target_height - avatar_height
            
        elif self.position == "left_in":
            # 左下内側（ターゲットウィンドウの左内側）
            new_x = target_x
            new_y = target_y + target_height - avatar_height
            
        elif self.position == "right_in":
            # 右下内側（ターゲットウィンドウの右内側）
            new_x = target_x + target_width - avatar_width
            new_y = target_y + target_height - avatar_height
            
        elif self.position == "right_out":
            # 右下外側（ターゲットウィンドウの右外側）
            new_x = target_x + target_width
            new_y = target_y + target_height - avatar_height
            
        else:
            logger.warning(f"Unknown position: {self.position}")
            return
        
        # ウィンドウを移動
        self.move(int(new_x), int(new_y))
        
    except Exception as e:
        logger.warning(f"Failed to update position: {e}")
        