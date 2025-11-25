from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseORM(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
