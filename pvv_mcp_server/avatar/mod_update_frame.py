"""
mod_update_frame.py
アニメーションフレームを更新するモジュール
"""

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


def update_frame(self) -> None:
    """
    self.label(QLabel)の画像を差し替える
    
    Args:
        self: AvatarWindowのインスタンス
              - self.pixmap_dict: anime_keyとQPixmapリストの連想配列
              - self.anime_key: 現在のアニメーションキー
              - self.anime_index: 現在のアニメーションインデックス
              - self.label: 画像を表示するQLabel
    
    Returns:
        None
    """
    # pixmap_dictが存在しない、または空の場合は何もしない
    if not hasattr(self, 'pixmap_dict') or not self.pixmap_dict:
        logger.warning("pixmap_dict is not initialized or empty")
        return
    
    # anime_keyが存在しない場合は何もしない
    if not hasattr(self, 'anime_key') or self.anime_key not in self.pixmap_dict:
        logger.warning(f"anime_key '{getattr(self, 'anime_key', None)}' not found in pixmap_dict")
        return
    
    # 画像リストを取得
    pixmap_list = self.pixmap_dict[self.anime_key][self.flip]
    
    # 画像リストが空の場合は何もしない
    if not pixmap_list:
        logger.warning(f"pixmap_list for anime_key '{self.anime_key}' is empty")
        return
    
    # anime_indexが存在しない場合は初期化
    if not hasattr(self, 'anime_index'):
        self.anime_index = 0
    
    # labelが存在しない場合は何もしない
    if not hasattr(self, 'label'):
        logger.warning("label (QLabel) is not initialized")
        return
    
    # 現在のインデックスの画像を取得
    current_pixmap = pixmap_list[self.anime_index]
    
    # QLabelに画像を設定
    self.label.setPixmap(current_pixmap)
    self.label.resize(current_pixmap.size())
    self.resize(current_pixmap.size())

    # インデックスをインクリメント（リストの長さを超えたら0に戻す）
    self.anime_index = (self.anime_index + 1) % len(pixmap_list)

