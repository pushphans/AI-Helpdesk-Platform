from datetime import datetime
from pydantic import EmailStr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, DateTime, UUID, func, Boolean
from ai_helpdesk_platform.core.db import Base
import uuid



class UserModel(Base):
    __tablename__ = "users"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key = True, nullable = False, default = uuid.uuid4)
    name : Mapped[str] = mapped_column(Text, nullable = False)
    email : Mapped[EmailStr] = mapped_column(Text, unique = True, nullable = False, index = True)
    password_hash : Mapped[str] = mapped_column(Text, nullable = False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), nullable = False)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), onupdate = func.now(), nullable = False)