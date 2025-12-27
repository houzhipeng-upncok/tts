from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime
import uuid
from user.models import User
from user.schemas import UserCreate, UserResponse

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """根据用户ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: UserCreate, password_hash: str) -> User:
        """创建新用户"""
        db_user = User(
            username=user_data.username,
            password_hash=password_hash,
            is_active=True
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_all_users(self) -> List[User]:
        """获取所有用户"""
        return self.db.query(User).all()

    def update_user(self, user_id: uuid.UUID, **kwargs) -> Optional[User]:
        """更新用户信息"""
        db_user = self.get_user_by_id(user_id)
        if db_user:
            for key, value in kwargs.items():
                if hasattr(db_user, key):
                    setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: uuid.UUID) -> bool:
        """删除用户"""
        db_user = self.get_user_by_id(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

    def update_last_login(self, user_id: uuid.UUID) -> Optional[User]:
        """更新用户最后登录时间"""
        return self.update_user(user_id, last_login_at=datetime.now())

    def is_user_active(self, user_id: uuid.UUID) -> bool:
        """检查用户是否活跃"""
        user = self.get_user_by_id(user_id)
        if user:
            return user.is_active
        return False

    def user_exists(self, username: str) -> bool:
        """检查用户是否存在"""
        return self.get_user_by_username(username) is not None