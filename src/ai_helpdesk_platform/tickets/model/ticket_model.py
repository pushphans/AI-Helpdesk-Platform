from datetime import datetime
from sqlalchemy import ForeignKey
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from ai_helpdesk_platform.core.db import Base
from sqlalchemy import Text, DateTime, func, Boolean, UUID
from enum import Enum



class TicketStatus(Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class TicketPriority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"





class TicketModel(Base):
    __tablename__ = "tickets"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key = True, nullable = False, default = uuid.uuid4)
    user_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique = True, index = True)
    title : Mapped[str] = mapped_column(Text, nullable = False)
    description : Mapped[str] = mapped_column(Text, nullable = False)
    status : Mapped[TicketStatus] = mapped_column(default = TicketStatus.OPEN, nullable = False)
    priority : Mapped[TicketPriority] = mapped_column(default = TicketPriority.MEDIUM, nullable = False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), nullable = False)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), onupdate = func.now(), nullable = False)
