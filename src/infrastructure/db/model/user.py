from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import enum


class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, nullable=False, index=True)

    hashed_password = Column(String, nullable=False)

    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(login={self.login}, role={self.role})>"