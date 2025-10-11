"""
MCP Server service module
MCPサーバクラスとToolsを定義する
"""
from mcp.server.fastmcp import FastMCP
from pvv_mcp_server import mod_speak
from pvv_mcp_server import mod_speak_metan_aska
from pvv_mcp_server import mod_speakers
from pvv_mcp_server import mod_speaker_info
import pvv_mcp_server.mod_avatar_manager
import json
from typing import Any
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import sys
from threading import Thread
import logging
import sys

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


mcp = FastMCP("pvv-mcp-server")
_config = None

@mcp.tool()
async def speak(
    style_id: int,
    msg: str,
    speedScale: float = 1.0,
    pitchScale: float = 0.0,
    intonationScale: float = 1.0,
    volumeScale: float = 1.0
) -> str:
    """
    VOICEVOX Web APIで音声合成し、音声を再生する
    
    Args:
        style_id: voicevox 発話音声を指定するID(必須)
        msg: 発話するメッセージ(必須)
        speedScale: 話速。デフォルト 1.0
        pitchScale: 声の高さ。デフォルト 0.0
        intonationScale: 抑揚の強さ。デフォルト 1.0
        volumeScale: 音量。デフォルト 1.0
    
    Returns:
        str: 実行結果メッセージ
    """
    try:
        # mod_speakのspeak関数を呼び出し
        mod_speak.speak(
            style_id=style_id,
            msg=msg,
            speedScale=speedScale,
            pitchScale=pitchScale,
            intonationScale=intonationScale,
            volumeScale=volumeScale
        )
        return f"音声合成・再生が完了しました。(style_id={style_id}, msg='{msg}')"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"


@mcp.tool()
async def speak_metan_aska(msg: str) -> str:
    """
    エヴァンゲリオンの「惣流・アスカ・ラングレー」として発話を行うツール。通常会話用。
    
    Args:
        msg: ユーザに伝える発話内容
    
    Returns:
        発話完了メッセージ
    """
    try:
        mod_speak_metan_aska.speak_metan_aska(msg)
        return f"発話完了: {msg}"
    except Exception as e:
        return f"エラー: {str(e)}"


@mcp.resource("voicevox://speakers")
def speakers() -> str:
    """
    VOICEVOX で利用可能な話者一覧を返す
    
    Returns:
        話者情報のJSON文字列
    """
    try:
        speaker_list = mod_speakers.speakers()
        return json.dumps(speaker_list, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"エラー: {str(e)}"


@mcp.resource("voicevox://speaker_info/{speaker_id}")
def speaker_info(speaker_id: str) -> str:
    """
    指定した話者の詳細情報を返す
    
    Args:
        speaker_id: 話者名またはUUID
    
    Returns:
        話者情報のJSON文字列
    """
    try:
        info = mod_speaker_info.speaker_info(speaker_id)
        return json.dumps(info, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"エラー: {str(e)}"


def start(conf: dict[str, Any]):
    """stdio モードで FastMCP を起動"""
    global _config 
    _config = conf

    if conf.get("avatar", {}).get("enabled"):
       start_mcp_avatar(conf.get("avatar"))
    else:
       start_mcp_avatar_disabled(conf.get("avatar"))

def start_mcp_avatar(conf: dict[str, Any]):
    logger.info("start_mcp_avatar called.")
    logger.debug(conf)

    Thread(target=start_mcp, args=(conf,), daemon=True).start()

    app = QApplication(sys.argv) 
    pvv_mcp_server.mod_avatar_manager.setup(conf) 
    sys.exit(app.exec())

def start_mcp(conf: dict[str, Any]):
    logger.info("start_mcp called.")
    logger.debug(conf)
    mcp.run(transport="stdio")

def start_mcp_avatar_disabled(conf: dict[str, Any]):
    logger.info("start_mcp_avatar_disabled")
    logger.debug(conf)
    pvv_mcp_server.mod_avatar_manager.setup(conf) 
    mcp.run(transport="stdio")

