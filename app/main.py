import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket

from app.core.kafka.producer import kafka_producer
from app.core.kafka.consumer import kafka_consumer
from app.core.setting import settings
from app.initialize.database import lifespan as database_lifespan
from app.initialize.websocket import socket_manage
from app.modules.auth.security import TokenService
from app.modules.clarius.server import start_grpc_server
from app.modules.user.controller import auth_router, user_router
from app.modules.user.dependencies import get_token_service


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Start DB
    async with database_lifespan(app):

        # Start GRPC
        grpc_task = asyncio.create_task(start_grpc_server())

        # Start global Kafka Producer
        await kafka_producer.start()
        await kafka_consumer.start()

        logging.info("Startup complete: DB + gRPC + Kafka Producer")

        yield

        # Shutdown Kafka
        await kafka_producer.stop()
        await kafka_consumer.stop()

        grpc_task.cancel()


class Application:
    def __init__(self):
        self.app = FastAPI(lifespan=app_lifespan)
        self.manager = socket_manage
        self.setup_router()
        self.init_cors()
        self.configure_logging()
        self.setup_websocket_router()

    def setup_router(self):
        """Define application routes here."""

        self.app.include_router(auth_router, prefix="/api/user", tags=["user"])
        self.app.include_router(user_router, prefix="/api/user", tags=["user"])

    def setup_websocket_router(self):
        """Define WebSocket routes here."""

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.manager.connect(websocket, "anonymous_user")
            try:
                while True:
                    await websocket.receive_json()
            except Exception as e:
                logging.info(f"WebSocket disconnected: {e}")
                self.manager.disconnect(websocket)

    def init_cors(self):
        """Set up CORS middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOW_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @staticmethod
    def configure_logging():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s : %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def start_app(self, host="0.0.0.0", port=8000):
        """Start the Uvicorn server."""
        uvicorn.run(self.app, host=host, port=port)


app_instance = Application()
app = app_instance.app

if __name__ == "__main__":
    # Run the application
    app_instance = Application()
    app_instance.start_app()
