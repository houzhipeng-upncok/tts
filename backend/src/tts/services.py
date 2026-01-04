import os
import asyncio
import time
import edge_tts
from typing import List

async def generate_tts_audio_simple(text: str, voice: str, output_file: str) -> None:
    """Edge-TTS实现"""
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"[日志] 创建输出目录: {output_dir}")
    
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"[日志] 清理旧文件: {output_file}")
        
    print(f"[日志] 开始生成TTS，文本长度: {len(text)}，声音类型: {voice}")
    
    # 获取实际使用的语音
    from .models import VOICE_MAPPING
    if voice in VOICE_MAPPING:
        actual_voice = VOICE_MAPPING[voice]
        print(f"[日志] 使用自定义映射: {voice} -> {actual_voice}")
    else:
        actual_voice = voice
        print(f"[日志] 直接使用Edge-TTS语音ID: {actual_voice}")
    
    # 定义备用语音列表，用于重试
    fallback_voices = {
        "zh-HK-HiuGaaiNeural": ["zh-HK-WanLungNeural", "zh-HK-HiuMaanNeural"],
        "zh-TW-HsiaoChenNeural": ["zh-TW-HsiaoYuNeural", "zh-TW-YunJheNeural"],
    }
    
    # 准备要尝试的语音列表
    voices_to_try = [actual_voice]
    if actual_voice in fallback_voices:
        voices_to_try.extend(fallback_voices[actual_voice])
    
    print(f"[日志] 将尝试的语音列表: {voices_to_try}")
    
    # 重试机制
    for i, voice_id in enumerate(voices_to_try):
        try:
            print(f"[日志] 第 {i+1}/{len(voices_to_try)} 次尝试，使用Edge-TTS，声音: {voice_id}")
            print(f"[日志] Edge-TTS输出路径: {output_file}")
            
            communicate = edge_tts.Communicate(
                text, 
                voice_id,
                rate='+0%',
                volume='+0%',
                pitch='+0Hz',
            )
            
            await asyncio.wait_for(communicate.save(output_file), timeout=60)
            print(f"[日志] Edge-TTS执行完成")
            
            if not os.path.exists(output_file):
                print(f"[错误] 生成的文件不存在: {output_file}")
                raise Exception("文件生成失败")
                
            file_size = os.path.getsize(output_file)
            print(f"[日志] Edge-TTS生成的文件大小: {file_size} 字节")
            
            if file_size < 1000:
                print(f"[警告] 生成的文件较小: {file_size} 字节，可能需要检查")
                
            print(f"[日志] 成功生成音频文件: {output_file}")
            
            # 成功生成，退出重试循环
            return
            
        except Exception as edge_tts_error:
            error_msg = f"[错误] Edge-TTS失败 (语音: {voice_id}): {str(edge_tts_error)}"
            print(error_msg)
            # 如果不是最后一次尝试，继续重试
            if i < len(voices_to_try) - 1:
                print(f"[日志] 将尝试下一个备用语音: {voices_to_try[i+1]}")
            else:
                print(f"[错误] 所有语音尝试均失败")
                # 所有尝试都失败，抛出异常
                raise

def cleanup_files(file_paths: List[str], delay_hours: int = 0) -> None:
    """清理临时文件，支持延迟清理"""
    if delay_hours > 0:
        print(f"[日志] 将在{delay_hours}小时后清理文件: {file_paths}")
        time.sleep(delay_hours * 3600)
    
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[日志] 已清理文件: {file_path}")
        except Exception as e:
            print(f"[警告] 清理文件 {file_path} 失败: {str(e)}")