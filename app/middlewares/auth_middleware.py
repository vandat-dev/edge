from uuid import UUID
import logging
from fastapi import HTTPException, Security
from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.constant.enums import UserRole
from app.core.app_status import AppStatus
from app.modules.user.model import User
from app.modules.user.dependencies import get_token_service, get_auth_repository
from app.modules.user.repository import AuthRepository
from app.modules.auth.security import TokenService
from app.utils.response import error_exception_handler

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


class AuthMiddleware:

    @classmethod
    async def get_current_user(cls,
                               credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                               token_service: TokenService = Depends(get_token_service),
                               auth_repo: AuthRepository = Depends(get_auth_repository)):
        try:
            token = credentials.credentials if credentials else None
            if not token:
                raise error_exception_handler(AppStatus.UNAUTHORIZED)

            claims = token_service.validate_token(token)
            if not claims:
                raise error_exception_handler(AppStatus.UNAUTHORIZED)

            user = await auth_repo.find_user_by_id(UUID(claims.get("sub")))
            if not user:
                raise error_exception_handler(AppStatus.UNAUTHORIZED)

            return user

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_current_user: {e}")
            raise error_exception_handler(AppStatus.UNAUTHORIZED)

    @classmethod
    def is_user(cls):
        async def dependency(auth_info: User = Depends(cls.get_current_user)):
            return auth_info

        return dependency

    @classmethod
    def is_admin(cls):
        async def dependency(current_user: User = Depends(cls.get_current_user)):
            if current_user.role != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail={
                    "error_code": AppStatus.FORBIDDEN.error_code,
                    "message": AppStatus.FORBIDDEN.message
                })
            return current_user

        return dependency

    @classmethod
    def is_fake(cls):
        async def dependency(auth_repo: AuthRepository = Depends(get_auth_repository)):
            user = await auth_repo.find_user_by_id(UUID("93add34e-4928-4430-9381-b5f9eb137283"))
            return user

        return dependency
