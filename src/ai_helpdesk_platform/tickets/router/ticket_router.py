from ai_helpdesk_platform.tickets.service.ticket_service import update_ticket
from ai_helpdesk_platform.tickets.schema.ticket_schema import UpdateTicketRequestSchema
from ai_helpdesk_platform.tickets.model.ticket_model import TicketPriority
from ai_helpdesk_platform.tickets.model.ticket_model import TicketStatus
from fastapi import Query
from ai_helpdesk_platform.tickets.service.ticket_service import list_tickets
from ai_helpdesk_platform.tickets.service.ticket_service import get_ticket
import uuid
from fastapi import status
from ai_helpdesk_platform.tickets.service.ticket_service import create_ticket
from ai_helpdesk_platform.auth.service.auth_service import get_user
from ai_helpdesk_platform.auth.model.users_model import UserModel
from ai_helpdesk_platform.core.db import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ai_helpdesk_platform.tickets.schema.ticket_schema import CreateTicketRequestSchema
from fastapi import APIRouter, HTTPException

ticket_router = APIRouter(prefix="/ticket", tags=["TICKET"])

@ticket_router.post("/create-ticket")
async def execute_create_ticket(
    data : CreateTicketRequestSchema,
    db : AsyncSession = Depends(get_db),
    user : UserModel = Depends(get_user)
):
    try:
        result = await create_ticket(data=data, db=db, user_id=user.id)
        return result

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )


@ticket_router.get("get-ticket/{ticket_id}")
async def execute_get_ticket(
    ticket_id : uuid.UUID,
    user : UserModel = Depends(get_user),
    db : AsyncSession = Depends(get_db)
):
    try:
        result = await get_ticket(user_id=user.id, db=db, ticket_id=ticket_id)
        return result
    
    except LookupError:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "No ticket found"
        )

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )
    
@ticket_router.get("list-tickets")
async def execute_list_tickets(
    user : UserModel = Depends(get_user),
    db : AsyncSession = Depends(get_db),
    page_size : int = Query(default=10, ge=10, le=100),
    page_number : int = Query(default=1, ge=1),
    search_term : str | None = None,
    status : TicketStatus | None = None,
    priority : TicketPriority | None = None

):
    try:
        result = await list_tickets(user_id=user.id, db=db, page_number=page_number, page_size=page_size, search_term=search_term, status=status, priority=priority)
        return result

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )
    


@ticket_router.put("/update-ticket/{ticket_id}")
async def execute_update_ticket(
    data : UpdateTicketRequestSchema,
    ticket_id : uuid.UUID,
    db : AsyncSession = Depends(get_db),
    user : UserModel = Depends(get_user),
):
    try:
        result = await update_ticket(user_id=user.id, data=data, db=db, ticket_id=ticket_id)

        return result

    except LookupError:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Ticket not found"
        )

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )


