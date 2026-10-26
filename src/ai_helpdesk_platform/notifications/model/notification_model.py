from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy import UUID
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, DateTime, func, Boolean
from ai_helpdesk_platform.core.db import Base



class NotificationModel(Base):
    __tablename__ = "notifications"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    message : Mapped[str] = mapped_column(Text, nullable=False)
    is_read : Mapped[bool] = mapped_column(Boolean, default=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False) 