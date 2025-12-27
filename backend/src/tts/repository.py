import os
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi.responses import FileResponse

def ensure_directories() -> None:
    """确保必要的目录存在"""
    os.makedirs('output', exist_ok=True)
    os.makedirs('temp', exist_ok=True)

def generate_output_filename() -> str:
    """生成唯一的输出文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"tts_{timestamp}_{unique_id}.mp3"

def get_file_path(filename: str) -> str:
    """获取文件的完整路径"""
    return os.path.join("output", filename)

def check_file_exists(file_path: str) -> bool:
    """检查文件是否存在"""
    return os.path.exists(file_path)

def get_file_size(file_path: str) -> int:
    """获取文件大小（字节）"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0

def create_file_response(filename: str) -> FileResponse:
    """创建文件响应"""
    file_path = get_file_path(filename)
    return FileResponse(
        file_path, 
        media_type="audio/mpeg", 
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )