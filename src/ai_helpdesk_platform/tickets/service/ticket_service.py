from ai_helpdesk_platform.tickets.schema.ticket_schema import UpdateTicketResponseSchema
from ai_helpdesk_platform.tickets.schema.ticket_schema import UpdateTicketRequestSchema
from ai_helpdesk_platform.tickets.schema.ticket_schema import UpdateTicketRequestSchema
from ai_helpdesk_platform.tickets.model.ticket_model import TicketPriority
from ai_helpdesk_platform.tickets.model.ticket_model import TicketStatus
from fastapi import Query
from sqlalchemy import select
from ai_helpdesk_platform.tickets.schema.ticket_schema import CreateTicketResponseSchema
from ai_helpdesk_platform.tickets.model.ticket_model import TicketModel
import uuid
from ai_helpdesk_platform.tickets.schema.ticket_schema import CreateTicketRequestSchema
from sqlalchemy.ext.asyncio import AsyncSession



async def create_ticket(
    db : AsyncSession,
    user_id : uuid.UUID,
    data : CreateTicketRequestSchema
):
    try:
        ticket = TicketModel(
        user_id = user_id,
        title = data.title,
        description = data.description,
        status = data.status,
        priority = data.priority
    )

        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)

        return CreateTicketResponseSchema(
            id=ticket.id,
            user_id=ticket.user_id,
            title=ticket.title,
            description=ticket.description,
            status=ticket.status,
            priority=ticket.priority,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at
        )

    except Exception:
        await db.rollback()
        raise


async def get_ticket(
    db : AsyncSession,
    user_id : uuid.UUID,
    ticket_id : uuid.UUID
):
    query = (
        select(TicketModel)
        .where(TicketModel.user_id == user_id, TicketModel.id == ticket_id)
        )

    result = await db.execute(query)

    ticket = result.scalar_one_or_none()

    if ticket is None:
        raise LookupError()

    return ticket



async def list_tickets(
    db : AsyncSession,
    user_id : uuid.UUID,
    page_size : int = Query(default=10, ge=10, le=100),
    page_number : int = Query(default=1, ge=1),
    search_term : str | None = None,
    status : TicketStatus | None = None,
    priority : TicketPriority | None = None
):
    query = (
        select(TicketModel)
        .where(TicketModel.user_id == user_id)
        )


    if search_term:
        query = query.where(TicketModel.title.ilike(f"%{search_term}%"))


    if status:
        query = query.where(TicketModel.status == status)

    if priority:
        query = query.where(TicketModel.priority == priority)

    offset = (page_number - 1) * page_size

    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)

    tickets = result.scalars().all()

    return tickets



async def update_ticket(
    db : AsyncSession,
    user_id : uuid.UUID,
    data : UpdateTicketRequestSchema,
    ticket_id : uuid.UUID
):
    try:
        query = (
            select(TicketModel)
            .where(TicketModel.user_id == user_id, TicketModel.id == ticket_id)
        )

        ticket_exists_result = await db.execute(query)

        ticket_exists = ticket_exists_result.scalar_one_or_none()


        if ticket_exists is None:
            raise LookupError()


        ticket_exists.title = data.title
        ticket_exists.description = data.description
        ticket_exists.status = data.status
        ticket_exists.priority = data.priority


        await db.commit()
        await db.refresh(ticket_exists)



        return UpdateTicketResponseSchema(
            id=ticket_exists.id,
            user_id=ticket_exists.user_id,
            title=ticket_exists.title,
            description=ticket_exists.description,
            status=ticket_exists.status,
            priority=ticket_exists.priority,
            created_at=ticket_exists.created_at,
            updated_at=ticket_exists.updated_at
        )

    except Exception:
        await db.rollback()
        raise








