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
    # 添加最新的香港粤语语音模型，根据Edge-TTS最新列表
    "zh-CN-Cantonese": "zh-HK-HiuGaaiNeural",  # 使用HiuGaai作为备用
    "zh-CN-Cantonese-2": "zh-HK-WanLungNeural",  # 男性粤语语音
    # 添加最新的台湾普通话语音模型
    "zh-CN-Taiwan": "zh-TW-HsiaoChenNeural",
    "zh-CN-Taiwan-2": "zh-TW-HsiaoYuNeural",
    "zh-CN-Taiwan-3": "zh-TW-YunJheNeural"
}