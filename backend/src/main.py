import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys
import os
from tts.routers import router as tts_router
from user.routers import router as user_router
from tts.repository import ensure_directories
from database import Base, engine
from dotenv import load_dotenv
import edge_tts

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


# 加载环境变量
load_dotenv()

app = FastAPI(
    title="地摊叫卖录音生成器 API",
    description="用于生成地摊叫卖/促销广告语录音的后端服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 注册路由
app.include_router(tts_router, prefix="/api")
app.include_router(user_router, prefix="/api/auth")

# 确保输出目录存在
output_dir = os.path.join(current_dir, "output")
os.makedirs(output_dir, exist_ok=True)

# 配置静态文件服务
app.mount("/output", StaticFiles(directory=output_dir), name="output")

# 应用启动时执行
@app.on_event("startup")
async def startup_event():
    ensure_directories()
    print(f"[启动] Edge-TTS版本: {edge_tts.__version__}")

if __name__ == "__main__":
    # 从环境变量获取配置
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )