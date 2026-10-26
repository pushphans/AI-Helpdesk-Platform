from ai_helpdesk_platform.notifications.schema.notification_schemas import UpdateNotificationRequestSchema
import uuid
from ai_helpdesk_platform.notifications.service.notification_service import mark_as_read
from ai_helpdesk_platform.notifications.service.notification_service import get_notifications
from fastapi import status
from fastapi import Query
from ai_helpdesk_platform.auth.model.users_model import UserModel
from ai_helpdesk_platform.auth.service.auth_service import get_user
from ai_helpdesk_platform.core.db import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException



notification_router = APIRouter(prefix="/notifications", tags=["NOTIFICATION"])

@notification_router.get("/get-notifications")
async def execute_get_notification(
    db : AsyncSession = Depends(get_db),
    user : UserModel = Depends(get_user),
    page_size : int = Query(default=10, ge=10, lt=100),
    page_number : int = Query(default=1, ge=1)
):
    try:
        result = await get_notifications(user_id=user.id, db=db, page_number=page_number, page_size=page_size)
        return result

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )



@notification_router.put("/mark-completed/{id}")
async def execute_mark_as_read(
    data : UpdateNotificationRequestSchema,
    id : uuid.UUID,
    user : UserModel = Depends(get_user),
    db : AsyncSession = Depends(get_db),
):
    try:
        result = await mark_as_read(user_id=user.id, db=db, data=data, id=id)
        return result

    except LookupError:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Notification not found"
        )

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )
