from ai_helpdesk_platform.notifications.schema.notification_schemas import UpdateNotificationResponseSchema
from ai_helpdesk_platform.notifications.schema.notification_schemas import UpdateNotificationRequestSchema
from sqlalchemy import select
from fastapi import Query
from ai_helpdesk_platform.notifications.schema.notification_schemas import CreateNotificationResponseSchema
from ai_helpdesk_platform.notifications.model.notification_model import NotificationModel
import uuid
from sqlalchemy.ext.asyncio import AsyncSession



async def create_notification(
    db : AsyncSession,
    user_id : uuid.UUID,
    message : str
):
    try:
        notification = NotificationModel(
            user_id = user_id,
            message = message
        )
        
        db.add(notification)
        await db.flush()

        return CreateNotificationResponseSchema(
            id=notification.id,
            user_id=notification.user_id,
            message=notification.message,
            is_read=notification.is_read,
            created_at=notification.created_at,
            updated_at=notification.updated_at
        )

    except Exception:
        await db.rollback()
        raise



async def get_notifications(
    db : AsyncSession,
    user_id : uuid.UUID,
    page_size : int = Query(default=10, ge=10, lt=100),
    page_number : int = Query(default=1, ge=1)
):
    query = (
        select(NotificationModel)
        .where(NotificationModel.user_id == user_id)
    )

    offset = (page_number - 1) * page_size

    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)

    notifications = result.scalars().all()

    return notifications



async def mark_as_read(
    db : AsyncSession,
    user_id : uuid.UUID,
    data : UpdateNotificationRequestSchema,
    id : uuid.UUID
):
    try:
        query = (
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id, NotificationModel.id == id)
        )

        result = await db.execute(query)

        notification = result.scalar_one_or_none()

        if notification is None:
            raise LookupError()

        notification.is_read = data.is_read

        await db.commit()
        await db.refresh(notification)

        return UpdateNotificationResponseSchema(
            id=notification.id,
            user_id=notification.user_id,
            message=notification.message,
            is_read=notification.is_read,
            created_at=notification.created_at,
            updated_at=notification.updated_at
        )

    except Exception:
        await db.rollback()
        raise
