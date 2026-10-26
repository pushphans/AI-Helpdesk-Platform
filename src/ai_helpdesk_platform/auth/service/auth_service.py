from fastapi import HTTPException
from ai_helpdesk_platform.auth.uitls.password_utils import password_hasher
from ai_helpdesk_platform.auth.uitls.password_utils import verify_hashed_password
from ai_helpdesk_platform.core.db import get_db
from fastapi import status
from fastapi.responses import JSONResponse
from ai_helpdesk_platform.auth.uitls.jwt_utils import decode_token
from fastapi import Depends
from ai_helpdesk_platform.auth.schema.auth_schema import RefreshTokenResponseModel
from ai_helpdesk_platform.auth.schema.auth_schema import RefreshTokenRequestSchema
from ai_helpdesk_platform.auth.schema.auth_schema import LoginResponseSchema
from datetime import timedelta
from datetime import timezone
from datetime import datetime
from ai_helpdesk_platform.auth.uitls.jwt_utils import create_refresh_token
from ai_helpdesk_platform.auth.model.refresh_token_model import RefreshTokenModel
from ai_helpdesk_platform.core.config import settings
from ai_helpdesk_platform.auth.uitls.jwt_utils import create_access_token
from ai_helpdesk_platform.auth.schema.auth_schema import LoginRequestSchema
from ai_helpdesk_platform.auth.schema.auth_schema import RegisterResponseSchema
from ai_helpdesk_platform.auth.uitls.password_utils import hash_passwrord
from sqlalchemy import select
from ai_helpdesk_platform.auth.model.users_model import UserModel
from ai_helpdesk_platform.auth.schema.auth_schema import RegisterRequestSchema
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class UserAlreadyExistsError(Exception):
    pass

class InvalidToken(Exception):
    pass

class InvalidCredentials(Exception):
    pass

class RefreshTokenExpiredError(Exception):
    pass




security = HTTPBearer()


async def register_user(
    db : AsyncSession,
    data : RegisterRequestSchema
):
    try:
        query = (
        select(UserModel)
        .where(UserModel.email == data.email)
    )

        result = await db.execute(query)

        user = result.scalar_one_or_none()

        if user:
            raise UserAlreadyExistsError()

        user = UserModel(
            name = data.name,
            email = data.email,
            password_hash = hash_passwrord(password=data.password)
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return RegisterResponseSchema(
            user_id=user.id,
            name = user.name,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    except Exception:
        await db.rollback()
        raise


async def login(
    db : AsyncSession,
    data : LoginRequestSchema
):
    try:
        query = (
            select(UserModel)
            .where(UserModel.email == data.email)
        )  

        result = await db.execute(query)

        user_exists = result.scalar_one_or_none()

        if user_exists is None:
            raise LookupError()

        password_verified = verify_hashed_password(hashed_password=user_exists.password_hash, password=data.password)

        if not password_verified:
            raise InvalidCredentials()
        
        access_token = await create_access_token(user_id=user_exists.id)
        access_token_expiry = settings.ACCESS_TOKEN_EXPIRY_IN_MINUTES * 60
        new_refresh_token = await create_refresh_token()
        new_refresh_token_expiry = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_IN_DAYS)


        rt_query = (
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_exists.id)
        )


        rt_result = await db.execute(rt_query)
        rt_object = rt_result.scalar_one_or_none()


        if rt_object is None:

            rt_object = RefreshTokenModel(
            refresh_token = new_refresh_token,
            rt_expiry = new_refresh_token_expiry,
            user_id = user_exists.id
            )


            db.add(rt_object)

        rt_object.refresh_token = new_refresh_token
        rt_object.rt_expiry = new_refresh_token_expiry


        await db.commit()
        await db.refresh(rt_object)

        return LoginResponseSchema(
            user_id=rt_object.user_id,
            name=user_exists.name,
            email=user_exists.email,
            access_token=access_token,
            access_token_expiry=access_token_expiry,
            refresh_token=rt_object.refresh_token,
            created_at=rt_object.created_at,
            updated_at=rt_object.updated_at
        )

    except Exception:
        await db.rollback()
        raise



async def refresh_token(
    db : AsyncSession,
    data : RefreshTokenRequestSchema
):
    try:
        query = (
        select(RefreshTokenModel)
        .where(RefreshTokenModel.refresh_token == data.refresh_token)
    )

        result = await db.execute(query)

        rt_exists = result.scalar_one_or_none()

        if rt_exists is None:
            raise InvalidToken()

        if rt_exists.rt_expiry <= datetime.now(timezone.utc):
            raise RefreshTokenExpiredError()

        new_refresh_token = await create_refresh_token()

        rt_exists.refresh_token = new_refresh_token
        rt_exists.rt_expiry = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_IN_DAYS)

        await db.commit()
        await db.refresh(rt_exists)

        new_access_token = await create_access_token(user_id=rt_exists.user_id)
        new_access_token_expiry = settings.ACCESS_TOKEN_EXPIRY_IN_MINUTES * 60


        return RefreshTokenResponseModel(
            user_id=rt_exists.user_id,
            access_token=new_access_token,
            refresh_token=rt_exists.refresh_token,
            access_token_expiry=new_access_token_expiry,
            created_at=rt_exists.created_at,
            updated_at=rt_exists.updated_at
        )

    except Exception:
        await db.rollback()
        raise



async def get_user(
    db : AsyncSession = Depends(get_db), 
    credentials : HTTPAuthorizationCredentials = Depends(security),
):

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    token = credentials.credentials
    payload = await decode_token(token=token)

    user_id = payload.get("sub")

    if user_id is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Invalid token"
        )

    query = (
        select(UserModel)
        .where(UserModel.id == user_id)
    )

    result = await db.execute(query)

    user = result.scalar_one_or_none()

    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    return user
    


 

    