import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from .models import TTSRequest
from .services import generate_tts_audio_simple, cleanup_files
from .repository import (
    generate_output_filename, 
    get_file_path, 
    check_file_exists, 
    get_file_size, 
    create_file_response
)

router = APIRouter(prefix="", tags=["TTS"])

@router.post("/generate")
async def generate_audio(request: TTSRequest, background_tasks: BackgroundTasks):
    """音频生成API"""
    print(f"[日志] 收到音频生成请求")
    
    if not request.text.strip():
        error_msg = "[错误] 文本不能为空"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    interval = request.interval if request.interval is not None else 0
    if interval < 0 or interval > 15:
        error_msg = "[错误] 间隔必须在0-15秒之间"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    if len(request.text) > 500:
        error_msg = "[错误] 文本长度不能超过500个字符"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    print(f"[日志] 请求参数 - 文本长度: {len(request.text)}, 声音: {request.voice}, BGM: {request.bgm}, 间隔: {interval}秒")
    
    output_filename = generate_output_filename()
    output_path = get_file_path(output_filename)
    
    print(f"[日志] 输出文件路径: {output_path}")
    
    try:
        print("[日志] 开始调用generate_tts_audio生成语音")
        await generate_tts_audio_simple(request.text, request.voice, output_path)
        print("[日志] TTS语音生成完成")
        
        if not check_file_exists(output_path):
            error_msg = "[错误] 语音文件生成失败，请稍后重试"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        final_size = get_file_size(output_path)
        print(f"[日志] 最终音频文件已生成，大小: {final_size} 字节")
        
        background_tasks.add_task(cleanup_files, [output_path], delay_hours=24)
        print("[日志] 已添加音频文件24小时后自动清理任务")
        
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
        error_msg = f"[错误] 音频生成过程中的错误: {str(e)}"
        print(error_msg)
        import traceback
        print(f"[错误] 异常堆栈: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"音频生成失败: {str(e)}")

@router.get("/api/output/{filename}")
async def get_output_file(filename: str):
    """获取生成的音频文件"""
    file_path = get_file_path(filename)
    if not check_file_exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return create_file_response(filename)

@router.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用地摊叫卖录音生成器 API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}