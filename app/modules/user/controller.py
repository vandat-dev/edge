import logging
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.app_status import AppStatus
from app.middlewares.auth_middleware import AuthMiddleware
from app.modules.user.dependencies import get_auth_service
from app.modules.user.schemas import LoginSchema, RegisterSchema, UserUpdateSchema, UserFilterSchema, RefreshTokenSchema
from app.modules.user.service import AuthService
from app.utils.response import handle_response

logger = logging.getLogger(__name__)
auth_router = APIRouter()
user_router = APIRouter()


@auth_router.post("/login")
async def login(user_login: LoginSchema,
                auth_service: AuthService = Depends(get_auth_service)):
    tokens = await auth_service.login(user_login.email, user_login.password)
    return handle_response(tokens)


@auth_router.get("/me")
async def me(user: AuthMiddleware = Depends(AuthMiddleware.get_current_user)):
    return user


@auth_router.post("/refresh")
async def refresh_token(refresh_data: RefreshTokenSchema,
                        auth_service: AuthService = Depends(get_auth_service)):
    tokens = await auth_service.refresh_token(refresh_data.refresh_token)
    return handle_response(tokens)


@auth_router.get("/producer")
async def producer(auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.send_user_created_event()
