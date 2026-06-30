from sqlalchemy import BigInteger, String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.core.database import Base
from app.models.base import TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "User"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    role: Mapped[str] = mapped_column(Enum("admin", "staff"), nullable=False, server_default="staff")
    status: Mapped[str] = mapped_column(Enum("active", "locked"), nullable=False, server_default="active")
