from ai_helpdesk_platform.ai.ticket_triage_agent.enums import TicketPriority
from ai_helpdesk_platform.ai.ticket_triage_agent.enums import TicketStatus
from pydantic import BaseModel



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