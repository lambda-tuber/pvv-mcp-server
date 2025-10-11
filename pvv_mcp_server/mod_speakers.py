"""
mod_speakers.py
VOICEVOX APIから話者一覧を取得する
"""
import requests
from typing import List, Dict, Any


# VOICEVOX APIのベースURL
VOICEVOX_URL = "http://localhost:50021"


def speakers() -> List[Dict[str, Any]]:
    """
    VOICEVOX APIから話者一覧を取得する
    
    Returns:
        話者情報のリスト
        各話者は以下の情報を含む:
        - name: 話者名
        - speaker_uuid: 話者のUUID
        - styles: スタイル情報のリスト（各スタイルにはnameとidが含まれる）
    
    Raises:
        requests.exceptions.RequestException: API呼び出しに失敗した場合
    """
    endpoint = f"{VOICEVOX_URL}/speakers"
    
    response = requests.get(endpoint)
    response.raise_for_status()
    
    return response.json()

if __name__ == "__main__":
    ret = speakers()
    print(ret)