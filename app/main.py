import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket

from app.core.kafka.delivery_messages import KafkaDeliveryMessages
from app.core.kafka.producer import kafka_producer
from app.core.kafka.consumer import kafka_consumer
from app.core.setting import settings
from app.initialize.database import lifespan as database_lifespan
from app.initialize.websocket import socket_manage
from app.modules.clarius.server import start_grpc_server
from app.modules.user.controller import auth_router, user_router


# ===========================================
# LIFESPAN (Startup / Shutdown)
# ===========================================
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with database_lifespan(app):

        # Start gRPC server (async)
        grpc_task = asyncio.create_task(start_grpc_server())

        # Kafka Consumer callback
        delivery_handler = KafkaDeliveryMessages()
        kafka_consumer.on_message(delivery_handler.handle)

        # Start Kafka Producer + Consumer
        await kafka_producer.start()
        await kafka_consumer.start()

        logging.info("Startup complete: DB + gRPC + Kafka Producer")

        # Give control back to FastAPI
        yield

        # Shutdown Kafka
        await kafka_producer.stop()
        await kafka_consumer.stop()

        # Shutdown gRPC
        grpc_task.cancel()
        try:
            await grpc_task
        except asyncio.CancelledError:
            logging.info("gRPC server stopped")


# ===========================================
# APPLICATION
# ===========================================
class Application:
    def __init__(self):
        self.app = FastAPI(lifespan=app_lifespan)
        self.manager = socket_manage

        self.configure_logging()
        self.init_cors()
        self.setup_router()
        self.setup_websocket_router()

    # -----------------------
    # ROUTES
    # -----------------------
    def setup_router(self):
        self.app.include_router(auth_router, prefix="/api/user", tags=["user"])
        self.app.include_router(user_router, prefix="/api/user", tags=["user"])

    # -----------------------
    # WEBSOCKET
    # -----------------------
    def setup_websocket_router(self):
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.manager.connect(websocket, "anonymous_user")
            try:
                while True:
                    await websocket.receive()   # nhận text / binary / ping / pong
            except Exception as e:
                logging.info(f"WebSocket disconnected: {e}")
                self.manager.disconnect(websocket)

    # -----------------------
    # CORS
    # -----------------------
    def init_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOW_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # -----------------------
    # LOGGING
    # -----------------------
    @staticmethod
    def configure_logging():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # -----------------------
    # START SERVER
    # -----------------------
    def start_app(self, host="0.0.0.0", port=8000):
        uvicorn.run(self.app, host=host, port=port)


# Export FastAPI app
app_instance = Application()
app = app_instance.app


# ===========================================
# MAIN
# ===========================================
if __name__ == "__main__":
    app_instance.start_app()
