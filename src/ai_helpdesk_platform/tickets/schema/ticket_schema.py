from datetime import datetime
import uuid
from ai_helpdesk_platform.tickets.model.ticket_model import TicketPriority
from ai_helpdesk_platform.tickets.model.ticket_model import TicketStatus
from pydantic import BaseModel, Field



class CreateTicketRequestSchema(BaseModel):
    title : str = Field(..., min_length=5, max_length=50)
    description : str = Field(..., max_length=200)
    status : TicketStatus = Field(default=TicketStatus.OPEN)
    priority : TicketPriority = Field(default=TicketPriority.MEDIUM)


class CreateTicketResponseSchema(BaseModel):
    id : uuid.UUID
    user_id : uuid.UUID
    title : str
    description : str
    status : TicketStatus
    priority : TicketPriority
    created_at : datetime
    updated_at : datetime




class UpdateTicketRequestSchema(BaseModel):
    title : str
    description : str
    status : TicketStatus
    priority : TicketPriority


class UpdateTicketResponseSchema(BaseModel):
    id : uuid.UUID
    user_id : uuid.UUID
    title : str
    description : str
    status : TicketStatus
    priority : TicketPriority
    created_at : datetime
    updated_at : datetime


class TriageAgentRequestSchema(BaseModel):
    title : str
    description : str
    status : TicketStatus
    priority : TicketPriority


class TriageAgentResponseSchema(BaseModel):
    category : str
    summary : str
    suggested_priority : TicketPriority
    suggested_reply : str
