from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import uuid
import os
from dotenv import load_dotenv
from user.repository import UserRepository
from user.models import User
from user.schemas import UserCreate, UserResponse, UserLogin
from database import get_db

# 加载环境变量
load_dotenv()

# 密码加密上下文 - 使用pbkdf2_sha256算法，避免bcrypt的问题
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# JWT配置 - 从环境变量获取
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        # bcrypt限制密码长度不能超过72字节
        if len(password) > 72:
            password = password[:72]
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[str]:
        """验证令牌并返回用户名"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None

    def register_user(self, user_data: UserCreate) -> tuple[bool, str, Optional[User]]:
        """用户注册"""
        # 检查用户名是否已存在
        if self.user_repo.user_exists(user_data.username):
            return False, "用户名已存在", None

        # 创建用户
        hashed_password = self.get_password_hash(user_data.password)
        
        # 使用repository创建用户记录
        db_user = self.user_repo.create_user(user_data, hashed_password)

        # 创建访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": db_user.username}, expires_delta=access_token_expires
        )

        return True, "注册成功", db_user

    def login_user(self, login_data: UserLogin) -> tuple[bool, str, Optional[str]]:
        """用户登录"""
        # 获取用户
        db_user = self.user_repo.get_user_by_username(login_data.username)
        if not db_user:
            return False, "用户名或密码错误", None

        # 检查用户是否活跃
        if not self.user_repo.is_user_active(db_user.id):
            return False, "用户已被禁用", None

        # 验证密码
        if not self.verify_password(login_data.password, db_user.password_hash):
            return False, "用户名或密码错误", None

        # 更新最后登录时间
        self.user_repo.update_last_login(db_user.id)

        # 创建访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": db_user.username}, expires_delta=access_token_expires
        )

        return True, "登录成功", access_token

    def get_current_user_from_token(self, token: str) -> Optional[User]:
        """从令牌获取当前用户"""
        username = self.verify_token(token)
        if not username:
            return None
        return self.user_repo.get_user_by_username(username)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """认证用户（简化版本）"""
        db_user = self.user_repo.get_user_by_username(username)
        if not db_user:
            return None
        if not self.user_repo.is_user_active(db_user.id):
            return None
        if not self.verify_password(password, db_user.password_hash):
            return None
        return db_user

    def get_user_info(self, user: User) -> dict:
        """获取用户信息"""
        return {
            "id": str(user.id),  # 转换为字符串以便JSON序列化
            "username": user.username,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "is_active": user.is_active
        }