from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from user.services import UserService
from user.schemas import UserCreate, UserLogin, AuthResponse, Token
from database import get_db

router = APIRouter()
security = HTTPBearer()

# 依赖项：获取当前用户
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_current_user_from_token(credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    service = UserService(db)
    success, message, user = service.register_user(user_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 创建访问令牌
    access_token_expires = service.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 转换为秒
    access_token = service.create_access_token(
        data={"sub": user.username}
    )
    
    return AuthResponse(
        message=message,
        user={
            "id": str(user.id),  # UUID转换为字符串
            "username": user.username,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "is_active": user.is_active
        },
        token=Token(
            access_token=access_token,
            token_type="bearer"
        )
    )

@router.post("/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    service = UserService(db)
    success, message, token = service.login_user(login_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    # 获取用户信息
    user = service.user_repo.get_user_by_username(login_data.username)
    
    return AuthResponse(
        message=message,
        user={
            "id": str(user.id),  # UUID转换为字符串
            "username": user.username,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "is_active": user.is_active
        },
        token=Token(
            access_token=token,
            token_type="bearer"
        )
    )

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    service = UserService(db)
    user_info = service.get_user_info(current_user)
    return user_info

@router.post("/logout")
async def logout_user():
    """用户登出（客户端删除token）"""
    return {"message": "登出成功"}