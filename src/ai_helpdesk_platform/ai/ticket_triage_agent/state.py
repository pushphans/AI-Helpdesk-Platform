from typing import TypedDict
from ai_helpdesk_platform.ai.ticket_triage_agent.enums import TicketPriority
from ai_helpdesk_platform.ai.ticket_triage_agent.enums import TicketStatus


class AgentState(TypedDict):
    # Ticket data
    title : str
    description : str
    status : TicketStatus
    priority : TicketPriority

    # Ticket analyzer
    category : str | None
    suggested_priority : TicketPriority | None
    summary : str | None

    # Find policy
    support_policy : str | None

    # suggested reply
    suggested_reply : str | None


