from sqlalchemy import Column, String, DateTime, Boolean, func, UUID
import uuid
from database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "tts"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(13), unique=True, index=True, nullable=False)  # 用户名最大13字符
    password_hash = Column(String(255), nullable=False)  # 存bcrypt hash，而不是明文
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"