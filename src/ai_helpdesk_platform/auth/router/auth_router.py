from ai_helpdesk_platform.auth.service.auth_service import RefreshTokenExpiredError
from ai_helpdesk_platform.auth.service.auth_service import InvalidCredentials
from ai_helpdesk_platform.auth.service.auth_service import InvalidToken
from ai_helpdesk_platform.auth.service.auth_service import refresh_token
from ai_helpdesk_platform.auth.schema.auth_schema import RefreshTokenRequestSchema
from ai_helpdesk_platform.auth.service.auth_service import login
from ai_helpdesk_platform.auth.schema.auth_schema import LoginRequestSchema
from fastapi import status
from ai_helpdesk_platform.auth.service.auth_service import UserAlreadyExistsError
from ai_helpdesk_platform.auth.service.auth_service import register_user
from ai_helpdesk_platform.auth.schema.auth_schema import RegisterRequestSchema
from ai_helpdesk_platform.core.db import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException

auth_router = APIRouter(prefix="/auth", tags=["AUTH"])

@auth_router.post("/register")
async def execute_register_user(
    data : RegisterRequestSchema,
    db : AsyncSession = Depends(get_db),
):
    try:
        result = await register_user(data=data, db=db)
        return result

    except UserAlreadyExistsError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Email already exists"
        )

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        ) 



@auth_router.post("/login")
async def execute_login(
    data : LoginRequestSchema,
    db : AsyncSession = Depends(get_db)
):
    try:
        result = await login(data=data, db=db)
        return result

    except LookupError:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Invalid credentials"
        )

    except InvalidCredentials:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid credentials"
        )



    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )



@auth_router.post("/refresh-token")
async def execute_refresh_token(
    data : RefreshTokenRequestSchema,
    db : AsyncSession = Depends(get_db)
):
    try:
        result = await refresh_token(db=db, data=data)
        return result

    except InvalidToken:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid token"
        )

    except RefreshTokenExpiredError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Refresh token expired"
        )

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )