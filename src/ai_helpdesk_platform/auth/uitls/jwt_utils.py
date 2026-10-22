import secrets
from ai_helpdesk_platform.core.config import settings
from datetime import timedelta
from datetime import timezone
from datetime import datetime
from uuid import UUID
import jwt



async def create_access_token(user_id : UUID):
    payload = {
        "sub" : str(user_id),
        "exp" : datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_IN_MINUTES)
    }

    token = jwt.encode(
        algorithm=settings.ALGORITHM,
        payload=payload,
        key=settings.JWT_SECRET_KEY
    )


    return token



async def decode_token(token : str):
    decoded_token = jwt.decode(
        token,
        key=settings.JWT_SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )

    return decoded_token



async def create_refresh_token():
    return secrets.token_urlsafe(64)