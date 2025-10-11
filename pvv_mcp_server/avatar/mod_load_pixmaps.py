"""
mod_load_pixmaps.py
アニメーション画像を事前に読み込むモジュール
"""

from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt, QByteArray, QBuffer

import os
import logging
import sys
import base64

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


def load_pixmaps(self, image_dict: dict, scale_percent: int = 100) -> dict:
    """
    アニメーション画像を事前に読み込んでおく
    
    Args:
        self: AvatarWindowのインスタンス
        image_dict: anime_keyとアニメーション画像リストの連想配列
                   例: {"idle": ["path/to/img1.png", "path/to/img2.png"], ...}
        scale_percent: 画像の縮尺変更パーセント値 (デフォルト: 100)
    
    Returns:
        dict: anime_key -> flip(bool) -> QPixmapリストの3階層辞書
              例: {"idle": {False: [QPixmap, ...], True: [QPixmap, ...]}, ...}
    """
    pixmap_dict = {}

    for anime_key, image_paths in image_dict.items():
        # 各anime_keyに対して、flipのTrue/Falseの辞書を作成
        pixmap_dict[anime_key] = {False: [], True: []}

        for image_source in image_paths:
            pixmap_original = QPixmap()

            if isinstance(image_source, str) and image_source.startswith("iVBOR"):
                try:
                    img_bytes = base64.b64decode(image_source)
                    byte_array = QByteArray(img_bytes)
                    buffer = QBuffer(byte_array)
                    buffer.open(QBuffer.ReadOnly)
                    if not pixmap_original.loadFromData(buffer.data()):
                        logger.warning("Failed to load Base64 image for key: %s", anime_key)
                        continue
                except Exception as e:
                    logger.warning("Exception decoding Base64 for key %s: %s", anime_key, e)
                    continue
            else:
                # ファイルとして読み込む
                if not os.path.exists(image_source):
                    logger.warning(f"Image file not found: {image_source}")
                    continue
                pixmap_original = QPixmap(image_source)
                if pixmap_original.isNull():
                    logger.warning(f"Failed to load image: {image_source}")
                    continue

            
            # スケーリング処理（元画像）
            if scale_percent != 100:
                new_width = int(pixmap_original.width() * scale_percent / 100)
                new_height = int(pixmap_original.height() * scale_percent / 100)
                pixmap_original = pixmap_original.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # 元画像をFalseに格納
            pixmap_dict[anime_key][False].append(pixmap_original)
            
            # 左右反転画像を作成
            transform = QTransform()
            transform.scale(-1, 1)
            pixmap_flipped = pixmap_original.transformed(transform, Qt.SmoothTransformation)
            
            # 反転画像をTrueに格納
            pixmap_dict[anime_key][True].append(pixmap_flipped)
    
    return pixmap_dict

    