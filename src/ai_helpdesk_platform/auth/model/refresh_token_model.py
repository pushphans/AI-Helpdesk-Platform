from sqlalchemy import ForeignKey
from datetime import datetime
import uuid
from ai_helpdesk_platform.core.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, DateTime, func, Boolean, UUID


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key = True, nullable = False, default = uuid.uuid4)
    user_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable = True, index = True)
    refresh_token : Mapped[str] = mapped_column(Text, nullable = False)
    rt_expiry : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable = False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), nullable = False)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), onupdate = func.now(), nullable = False)