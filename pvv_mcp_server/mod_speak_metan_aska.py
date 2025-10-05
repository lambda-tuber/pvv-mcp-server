# mod_speak_metan_aska.py

import requests
import sounddevice as sd
import soundfile as sf
import numpy as np
import io

def speak_metan_aska(msg: str) -> None:
    """
    四国めたん(style_id=6)を使用してVOICEVOX Web APIで音声合成し、再生する関数
    
    Args:
        msg (str): 発話するメッセージ
    
    Returns:
        None

    Example:
        python -c "from pvv_mcp_server.mod_speak_metan_aska import speak_metan_aska; speak_metan_aska('あんた、バカぁ！？')"

    """
    # VOICEVOXのデフォルトURL
    pvv_url = "http://127.0.0.1:50021"
    style_id = 6  # 四国めたん
    
    # 音声合成用クエリの作成
    query_url = f"{pvv_url}/audio_query"
    query_params = {
        "text": msg,
        "speaker": style_id
    }
    
    # クエリ生成
    query_response = requests.post(query_url, params=query_params)
    query_response.raise_for_status()
    query_data = query_response.json()
    
    # 音声合成
    synthesis_url = f"{pvv_url}/synthesis"
    synthesis_params = {
        "speaker": style_id
    }
    synthesis_response = requests.post(
        synthesis_url,
        params=synthesis_params,
        json=query_data
    )
    synthesis_response.raise_for_status()
    
    audio_data, samplerate = sf.read(io.BytesIO(synthesis_response.content), dtype='float32', always_2d=True)
    with sd.OutputStream(samplerate=samplerate, channels=audio_data.shape[1], dtype='float32') as stream:
        stream.write(audio_data)
