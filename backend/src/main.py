from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
import edge_tts
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from sqlalchemy import text

from database import Base, engine
from tts.routers import router as tts_router
from user.routers import router as user_router
from tts.repository import ensure_directories

# --------------------------------------------------
# 基础环境准备
# --------------------------------------------------

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

load_dotenv()

APP_VERSION = "1.0.0"


# --------------------------------------------------
# Lifespan（替代 on_event）
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # 启动时
    ensure_directories()
    Base.metadata.create_all(bind=engine)
    print(f"[启动] Edge-TTS 版本: {edge_tts.__version__}")

    yield

    # 关闭时（目前无需处理）
    print("[关闭] 应用关闭")


# --------------------------------------------------
# Application Factory
# --------------------------------------------------

def create_application() -> FastAPI:
    app = FastAPI(
        title="地摊叫卖录音生成器 API",
        description="用于生成地摊叫卖 / 促销广告语录音的后端服务",
        version=APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    _register_middlewares(app)
    _register_system_routes(app)
    _register_domain_routes(app)
    _register_static(app)

    return app


# --------------------------------------------------
# Middlewares
# --------------------------------------------------

def _register_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# --------------------------------------------------
# 系统路由（health）
# --------------------------------------------------

def _register_system_routes(app: FastAPI) -> None:
    router = APIRouter(prefix="/api")

    @router.get("/health", tags=["system"])
    async def health():
        # 数据库连通性检测
        db_status = "ok"
        db_detail = None
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as e:
            db_status = "error"
            db_detail = str(e)

        return {
            "version": APP_VERSION,
            "postgres": {
                "status": db_status,
                "detail": db_detail,
            },
        }

    app.include_router(router)


# --------------------------------------------------
# 业务路由
# --------------------------------------------------

def _register_domain_routes(app: FastAPI) -> None:
    # /api/xxx
    app.include_router(tts_router, prefix="/api", tags=["tts"])

    # /api/auth/xxx
    app.include_router(user_router, prefix="/api/auth", tags=["auth"])


# --------------------------------------------------
# 静态文件
# --------------------------------------------------

def _register_static(app: FastAPI) -> None:
    # 项目根目录下的 output 目录，而不是 src 目录下的 output 目录
    output_dir = os.path.join(os.path.dirname(current_dir), "output")
    os.makedirs(output_dir, exist_ok=True)
    app.mount("/output", StaticFiles(directory=output_dir), name="output")


# --------------------------------------------------
# ASGI app
# --------------------------------------------------

app: FastAPI = create_application()


# --------------------------------------------------
# 本地启动
# --------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True,
    )
