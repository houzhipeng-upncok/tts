from pydantic import BaseModel

class TTSRequest(BaseModel):
    text: str
    voice: str
    bgm: str = ""
    interval: int = 0

VOICE_MAPPING = {
    "zh-CN-YunyangNeural": "zh-CN-YunyangNeural",
    "zh-CN-XiaoxiaoNeural": "zh-CN-XiaoxiaoNeural",
    "zh-CN-XiaoyiNeural": "zh-CN-XiaoyiNeural",
    "zh-CN-YunjianNeural": "zh-CN-YunjianNeural",
    "zh-CN-YunxiNeural": "zh-CN-YunxiNeural",
    "zh-CN-YunxiaNeural": "zh-CN-YunxiaNeural",
    "zh-CN-Cantonese": "zh-HK-HiuMaanNeural",
    "zh-CN-Taiwan": "zh-TW-HsiaoChenNeural"
}