"""
mod_speaker_info.py
voicevox web apiでspeaker情報を取得する。
"""
import requests
from typing import Dict, Any
from pvv_mcp_server.mod_speakers import speakers


def speaker_info(speaker_id: str) -> Dict[str, Any]:
    """
    voicevox web apiでspeaker情報を取得する。
    
    Args:
        speaker_id: 文字列。話者名、または、UUID。
    
    Returns:
        Dict[str, Any]: 話者情報
    
    Raises:
        ValueError: 話者が見つからない場合
        requests.RequestException: APIリクエストが失敗した場合
    """
    VOICEVOX_API_BASE = "http://localhost:50021"
    
    # UUIDかどうかをチェック（簡易的に `-` を含むかで判定）
    if "-" in speaker_id:
        # UUIDの場合、直接APIリクエスト
        uuid = speaker_id
    else:
        # 話者名の場合、speakers関数で話者リストを取得して検索
        speakers_list = speakers()
        
        # 話者名が部分一致する話者を検索
        matched_speaker = None
        for speaker in speakers_list:
            if speaker_id.lower() in speaker["name"].lower():
                matched_speaker = speaker
                break
        
        if matched_speaker is None:
            raise ValueError(f"話者 '{speaker_id}' が見つかりませんでした。")
        
        uuid = matched_speaker["speaker_uuid"]
    
    # speaker_info APIをリクエスト
    url = f"{VOICEVOX_API_BASE}/speaker_info"
    params = {"speaker_uuid": uuid}
    #print(params)
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 音声、base64画像データを省略
        # if "portrait" in data and data["portrait"]:
        #     data["portrait"] = "[画像データ省略]"
        
        # if "style_infos" in data:
        #     for style in data["style_infos"]:
        #         if "icon" in style and style["icon"]:
        #             style["icon"] = "[画像データ省略]"
        #         if "portrait" in style and style["portrait"]:
        #             style["portrait"] = "[画像データ省略]"
        #         if "voice_samples" in style and style["voice_samples"]:
        #             style["voice_samples"] = ["[サンプル音声データ省略]"]

        return data

    except requests.RequestException as e:
        raise requests.RequestException(f"speaker_info APIリクエストが失敗しました: {e}")

if __name__ == "__main__":
    ret = speaker_info("四国")
    print(ret)
