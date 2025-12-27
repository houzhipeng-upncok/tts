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
    
    try:
        print(f"[日志] 使用Edge-TTS，声音: {actual_voice}")
        print(f"[日志] Edge-TTS输出路径: {output_file}")
        
        communicate = edge_tts.Communicate(
            text, 
            actual_voice,
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
            
    except Exception as edge_tts_error:
        error_msg = f"[错误] Edge-TTS失败: {str(edge_tts_error)}"
        print(error_msg)
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