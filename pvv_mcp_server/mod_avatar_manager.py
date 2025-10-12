"""
mod_avatar_manager.py
アバター管理モジュール（リファクタリング版）
"""

import json
import sys
import logging
from typing import Any, Dict, Optional
from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Q_ARG, Q_RETURN_ARG

from pvv_mcp_server.avatar.mod_avatar import AvatarWindow
from pvv_mcp_server.mod_speaker_info import speaker_info

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# stderrへの出力ハンドラー
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# グローバル変数
_avatar_config: Optional[Dict[str, Any]] = None
_avatars_config: Optional[Dict[int, Any]] = None
_avatar_cache: Dict[int, AvatarWindow] = {}


# ==================== Public API ====================

def setup(avs: Dict[int, Any]) -> None:
    """
    アバターマネージャーの初期化
    
    Args:
        avs: アバター設定の辞書
            - enabled: アバター機能の有効/無効
            - target: アプリケーション名
            - avatars: style_id毎のアバター設定
    """
    global _avatar_config, _avatars_config
    
    _avatar_config = avs
    _avatars_config = avs.get("avatars", {})
    
    if _avatar_config.get("enabled"):
        logger.info("Avatar enabled. Creating all avatar instances...")
        _create_all_avatars()
        logger.info(f"Created {len(_avatar_cache)} avatar instance(s).")
    else:
        logger.info("Avatar disabled.")


def set_anime_key(style_id: int, anime_key: str) -> None:
    """
    指定されたアバターのアニメーションキーを設定
    
    Args:
        style_id: スタイルID
        anime_key: アニメーションキー（"立ち絵", "口パク"など）
    """
    if not _avatar_config or not _avatar_config.get("enabled"):
        logger.info("Avatar disabled. Skipping set_anime_key.")
        return
    
    avatar = _get_avatar(style_id)
    if avatar:
        QMetaObject.invokeMethod(avatar, "showWindow", Qt.ConnectionType.QueuedConnection)
        QMetaObject.invokeMethod(avatar, "set_anime_key", Qt.ConnectionType.QueuedConnection, Q_ARG(str, anime_key))
    else:
        logger.warning(f"Avatar not found for style_id={style_id}")


# ==================== Private Functions ====================

def _create_all_avatars() -> None:
    """
    設定に登録されているすべてのアバターインスタンスを作成
    """
    if not _avatars_config:
        logger.warning("No avatars configured.")
        return
    
    for style_id, avatar_conf in _avatars_config.items():
        try:
            _create_avatar(style_id, avatar_conf)
            logger.info(f"Created avatar for style_id={style_id}")
        except Exception as e:
            logger.error(f"Failed to create avatar for style_id={style_id}: {e}")


def _create_avatar(style_id: int, avatar_conf: Dict[str, Any]) -> AvatarWindow:
    """
    個別のアバターインスタンスを作成
    
    Args:
        style_id: スタイルID
        avatar_conf: アバター設定
    
    Returns:
        作成されたAvatarWindowインスタンス
    """
    # 画像データの取得
    images = _get_images(
        avatar_conf.get("話者", ""),
        avatar_conf.get("画像", {})
    )

    # アバターインスタンスの作成
    instance = AvatarWindow(
        images,
        default_anime_key="立ち絵",
        flip=avatar_conf.get("反転", False),
        scale_percent=avatar_conf.get("縮尺", 50),
        app_title=_avatar_config.get("target", "Claude"),
        position=avatar_conf.get("位置", "right_out")
    )
    
    # 位置更新と表示設定
    instance.update_position()
    if avatar_conf.get("表示", False):
        instance.show()
    else:
        instance.hide()

    # キャッシュに登録
    # style_idが違っても、avatar_confは参照で同一の場合は、同一avatarとして扱う必要がある。
    key = json.dumps(avatar_conf, sort_keys=True)
    _avatar_cache[key] = instance
    
    return instance


def _get_avatar(style_id: int) -> Optional[AvatarWindow]:
    """
    キャッシュからアバターインスタンスを取得
    
    Args:
        style_id: スタイルID
    
    Returns:
        AvatarWindowインスタンス、存在しない場合はNone
    """

    avatar_conf = _avatars_config.get(style_id)
    key = json.dumps(avatar_conf, sort_keys=True)
    return _avatar_cache.get(key)


def _get_images(speaker_id: str, images: Dict[str, list]) -> Dict[str, list]:
    """
    アバター画像データの取得
    
    Args:
        speaker_id: 話者ID
        images: 画像設定辞書
    
    Returns:
        画像データ辞書
    """
    # 既に画像が設定されている場合はそのまま返す
    if images.get("立ち絵"):
        return images
    
    # speaker_infoからポートレートを取得
    info = speaker_info(speaker_id)
    b64dat = info.get("portrait")
    
    if not b64dat:
        logger.warning(f"speaker_id={speaker_id}: portrait not found in speaker_info")
        return images
    
    # デフォルトポートレートを設定
    ret = images.copy()
    ret["立ち絵"] = [b64dat]
    ret["口パク"] = [b64dat]
    
    logger.debug(f"Using VOICEVOX default portrait for speaker_id={speaker_id}")
    return ret


# ==================== Test Entry Point ====================

if __name__ == "__main__":
    print("Testing mod_avatar_manager...")
    
    # テスト用設定
    test_config = {
        "enabled": True,
        "target": "TestApp",
        "avatars": {
            2: {
                "話者": "四国めたん",
                "表示": True,
                "画像": {},
                "反転": False,
                "縮尺": 50,
                "位置": "right_out"
            }
        }
    }
    
    setup(test_config)
    set_anime_key(2, "口パク")
    
    print("Test completed.")