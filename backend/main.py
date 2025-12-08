import os
import tempfile
import asyncio
import uuid
import shutil
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import edge_tts
from pydantic import BaseModel

# 确保必要的目录存在
os.makedirs('output', exist_ok=True)
os.makedirs('temp', exist_ok=True)

app = FastAPI(
    title="地摊叫卖录音生成器 API",
    description="用于生成地摊叫卖/促销广告语录音的后端服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class TTSRequest(BaseModel):
    text: str
    voice: str
    bgm: str = ""  # 设为可选，默认为空字符串
    interval: int = 0  # 设为可选，默认为0

# 语音映射配置 - 只映射自定义标识符，保留直接的Edge-TTS语音ID不变
VOICE_MAPPING = {
    "zh-CN-YunyangNeural": "zh-CN-XiaoqiuNeural",  # 女声（沉稳）
    "zh-CN-Shandong": "zh-CN-shandong-YunxiangNeural",  # 山东方言
    "zh-CN-Sichuan": "zh-CN-sichuan-YunxiNeural",  # 四川方言
    "zh-CN-Northeast": "zh-CN-liaoning-XiaobeiNeural",  # 东北方言
    "zh-CN-Cantonese": "zh-HK-HiuGaaiNeural",  # 粤语
    "zh-CN-Taiwan": "zh-TW-HsiaoYuNeural"  # 台湾方言
}

async def generate_tts_audio_simple(text: str, voice: str, output_file: str) -> None:
    """Edge-TTS实现"""
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"[日志] 创建输出目录: {output_dir}")
    
    # 清理可能存在的旧文件
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"[日志] 清理旧文件: {output_file}")
        
    print(f"[日志] 开始生成TTS，文本长度: {len(text)}，声音类型: {voice}")
    
    # 获取实际使用的语音 - 只对自定义标识符进行映射
    # 直接的Edge-TTS语音ID（如zh-CN-XiaoxiaoNeural）保持不变
    if voice in VOICE_MAPPING:
        actual_voice = VOICE_MAPPING[voice]
        print(f"[日志] 使用自定义映射: {voice} -> {actual_voice}")
    else:
        actual_voice = voice
        print(f"[日志] 直接使用Edge-TTS语音ID: {actual_voice}")
    
    # 直接使用Edge-TTS
    try:
        print(f"[日志] 使用Edge-TTS，声音: {actual_voice}")
        print(f"[日志] Edge-TTS输出路径: {output_file}")
        
        # 创建Edge-TTS实例
        communicate = edge_tts.Communicate(
            text, 
            actual_voice,
            rate='+0%',
            volume='+0%',
            pitch='+0Hz',
        )
        
        # 执行保存操作，设置合理的超时
        await asyncio.wait_for(communicate.save(output_file), timeout=60)
        print(f"[日志] Edge-TTS执行完成")
        
        # 验证文件是否生成
        if not os.path.exists(output_file):
            print(f"[错误] 生成的文件不存在: {output_file}")
            raise Exception("文件生成失败")
            
        file_size = os.path.getsize(output_file)
        print(f"[日志] Edge-TTS生成的文件大小: {file_size} 字节")
        
        # 基本文件大小检查
        if file_size < 1000:
            print(f"[警告] 生成的文件较小: {file_size} 字节，可能需要检查")
            
        print(f"[日志] 成功生成音频文件: {output_file}")
            
    except Exception as edge_tts_error:
        error_msg = f"[错误] Edge-TTS失败: {str(edge_tts_error)}"
        print(error_msg)
        raise

def cleanup_files(file_paths: list, delay_hours: int = 0):
    """清理临时文件，支持延迟清理"""
    import time
    # 如果指定了延迟时间，则等待
    if delay_hours > 0:
        print(f"[日志] 将在{delay_hours}小时后清理文件: {file_paths}")
        time.sleep(delay_hours * 3600)  # 转换为秒
    
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[日志] 已清理文件: {file_path}")
        except Exception as e:
            print(f"[警告] 清理文件 {file_path} 失败: {str(e)}")

@app.post("/api/generate")
async def generate_audio(request: TTSRequest, background_tasks: BackgroundTasks):
    """音频生成API"""
    print(f"[日志] 收到音频生成请求")
    
    # 验证输入
    if not request.text.strip():
        error_msg = "[错误] 文本不能为空"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 检查并设置默认间隔值
    interval = request.interval if request.interval is not None else 0
    if interval < 0 or interval > 15:
        error_msg = "[错误] 间隔必须在0-15秒之间"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 限制文本长度
    if len(request.text) > 500:
        error_msg = "[错误] 文本长度不能超过500个字符"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    print(f"[日志] 请求参数 - 文本长度: {len(request.text)}, 声音: {request.voice}, BGM: {request.bgm}, 间隔: {interval}秒")
    
    # 生成唯一的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    output_filename = f"tts_{timestamp}_{unique_id}.mp3"
    output_path = os.path.join("output", output_filename)
    
    print(f"[日志] 输出文件路径: {output_path}")
    
    # 临时文件路径 - 虽然当前实现不使用临时文件，但保留以备将来扩展
    # temp_voice_file = os.path.join("temp", f"voice_{unique_id}.mp3")
    
    try:
        # 1. 直接生成最终的音频文件，不进行中间处理
        try:
            print("[日志] 开始调用generate_tts_audio生成语音")
            await generate_tts_audio_simple(request.text, request.voice, output_path)
            print("[日志] TTS语音生成完成")
        except Exception as tts_error:
            error_msg = f"[错误] TTS生成失败: {str(tts_error)}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=f"语音生成失败: {str(tts_error)}")
        
        # 检查文件是否成功生成
        if not os.path.exists(output_path):
            error_msg = "[错误] 语音文件生成失败，请稍后重试"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        final_size = os.path.getsize(output_path)
        print(f"[日志] 最终音频文件已生成，大小: {final_size} 字节")
        
        # 当前实现不使用临时文件，跳过临时文件清理
            
        # 为生成的音频文件添加24小时后自动清理任务
        background_tasks.add_task(cleanup_files, [output_path], delay_hours=24)
        print("[日志] 已添加音频文件24小时后自动清理任务")
        
        # 返回音频文件的URL和相关信息
        response = {
            "url": f"/output/{output_filename}",
            "filename": output_filename,
            "size": final_size,
            "message": "音频文件生成成功"
        }
        print(f"[日志] 音频生成完成，返回URL: {response['url']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        # 记录详细错误
        error_msg = f"[错误] 音频生成过程中的错误: {str(e)}"
        print(error_msg)
        import traceback
        print(f"[错误] 异常堆栈: {traceback.format_exc()}")
        # 当前实现不使用临时文件，跳过临时文件清理
        # 抛出HTTP异常
        raise HTTPException(status_code=500, detail=f"音频生成失败: {str(e)}")

@app.get("/output/{filename}")
async def get_output_file(filename: str):
    """获取生成的音频文件"""
    file_path = os.path.join("output", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 设置适当的MIME类型
    return FileResponse(file_path, media_type="audio/mpeg")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用地摊叫卖录音生成器 API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print(f"[启动] Edge-TTS版本: {edge_tts.__version__}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
