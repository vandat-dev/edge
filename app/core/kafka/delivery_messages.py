import logging
from app.modules.user.factory import create_auth_service
from app.modules.user.service import AuthService


class KafkaDeliveryMessages:
    def __init__(self):
        self.auth_service: AuthService | None = None

    async def init(self):
        if self.auth_service is None:
            self.auth_service = await create_auth_service()

    async def handle(self, data: dict):
        await self.init()

        logging.info(f"[DELIVERY] Received: {data}")
        await self.auth_service.receive_messages(data)
