
import json
import sys
import logging
from typing import List
from typing import Any
from typing import Dict

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

_avatar = None
_avatars = None
_avatar_cache: dict[str, AvatarWindow] = {}

def setup(avs: dict[int, Any]):
    global _avatar
    _avatar = avs
    global _avatars
    _avatars = avs.get("avatars", {})

    if _avatar.get("enabled"):
        for style_id, info in _avatars.items():
            get_avatar(style_id, info.get("表示"))


def set_anime_key(style_id: int, anime_key: str):
    if not _avatar.get("enabled"):
        logger.info("unexpected function call. avatar disabled.")
        return 

    if style_id in _avatars:
        get_avatar(style_id, True).set_anime_key(anime_key)


def get_avatar(style_id: int, visible: bool) -> AvatarWindow:
    if not _avatar.get("enabled"):
        logger.info("unexpected function call. avatar disabled.")
        return 

    avatar_conf = _avatars.get(style_id, {})
    key = json.dumps(avatar_conf, sort_keys=True)

    if key in _avatar_cache:
        logger.info("cache instance found.")
        instance = _avatar_cache[key]
        if visible:
            instance.show()
        return instance

    images = get_images(avatar_conf.get("話者"), avatar_conf.get("画像", []))
    instance = AvatarWindow(
        images,
        default_anime_key="立ち絵",
        flip=avatar_conf.get("反転", False),
        scale_percent=avatar_conf.get("縮尺", 50),
        app_title=_avatar.get("target","Claude"),
        position=avatar_conf.get("位置","right_out")
    )
    instance.update_position()
    instance.show() # 一旦showしておくと、後々、FastMCPスレッドから、show/hideができる。
    if not visible:
        instance.hide()
    _avatar_cache[key] = instance

    return instance

  
def get_images(speaker_id: str, images: Dict[str, List[str]]) -> Dict[str, List[str]]:
    if images.get("立ち絵"):
        return images

    info = speaker_info(speaker_id)
    b64dat = info.get("portrait")

    if not b64dat:
        logger.warning(f"speaker_id={speaker_id}: portrait not found in speaker_info")
        return images

    ret = images.copy()
    ret["立ち絵"] = [b64dat]
    ret["口パク"] = [b64dat]

    logger.debug("voicevox default portrait: " + str(ret))
    return ret

# ----------------------------
if __name__ == "__main__":

  print("test")
  dat = {
    "立ち絵" : [],
    "口パク" : []
  }
  bdat = get_images("冥鳴ひまり", dat)
  print(bdat)
