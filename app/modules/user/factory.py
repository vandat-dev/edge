from app.initialize.database import get_session
from app.modules.user.dependencies import get_auth_repository, get_token_service
from app.modules.user.service import AuthService


# async def create_auth_service():
#     async for db in get_session():
#         repo = get_auth_repository(db)
#         token = get_token_service()
#         return AuthService(repo, token)

class EmptyRepo:
    pass

async def create_auth_service():
    repo = EmptyRepo()
    token = get_token_service()
    return AuthService(repo, token)
