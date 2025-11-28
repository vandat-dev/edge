"""gRPC server startup and management for Clarius service."""
import logging

import grpc

from app.modules.clarius.config import GRPC_ADDRESS, GRPC_PORT
from app.modules.clarius.proto import frame_pb2_grpc
from app.modules.clarius.servicer import FrameServicer

logger = logging.getLogger(__name__)


async def start_grpc_server():
    """
    Start the Clarius gRPC server.

    This function initializes and starts the gRPC server on the configured port.
    It should be called as a background task during application startup.
    """
    server = grpc.aio.server()

    # Create and register the servicer
    servicer = FrameServicer()
    frame_pb2_grpc.add_FrameServiceServicer_to_server(servicer, server)

    # Add port and start
    server.add_insecure_port(GRPC_ADDRESS)
    logger.info(f"Clarius gRPC server starting on port {GRPC_PORT}...")

    await server.start()
    await server.wait_for_termination()
