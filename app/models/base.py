from sqlalchemy import DateTime, func
from sqlalchemy.orm import declarative_mixin, Mapped, mapped_column
from datetime import datetime
from typing import Optional

@declarative_mixin
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=True)
