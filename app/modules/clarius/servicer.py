"""gRPC servicer implementation for Clarius frame service."""
import asyncio
import base64
import logging

import grpc

from app.modules.clarius.proto import frame_pb2, frame_pb2_grpc
from app.initialize.websocket import socket_manage

logger = logging.getLogger(__name__)


class FrameServicer(frame_pb2_grpc.FrameServiceServicer):
    """Servicer for handling frame data from Clarius."""

    async def SendFrame(
            self, request: frame_pb2.FrameRequest, context: grpc.aio.ServicerContext
    ) -> frame_pb2.FrameResponse:
        try:
            # print("Received frame")
            asyncio.create_task(socket_manage.broadcast_binary(request.data))
            return frame_pb2.FrameResponse()
            # await socket_manage.broadcast_binary(request.data)
            # logger.debug("Frame broadcasted successfully")
            # return frame_pb2.FrameResponse()

        except Exception as e:
            logger.error(f"Error processing frame: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return frame_pb2.FrameResponse()

    # async def SendFrame(
    #     self, request: frame_pb2.FrameRequest, context: grpc.aio.ServicerContext
    # ) -> frame_pb2.FrameResponse:
    #     """
    #     Handle incoming frame data.
    #
    #     Args:
    #         request: FrameRequest containing frame data
    #         context: gRPC context
    #
    #     Returns:
    #         FrameResponse (empty response)
    #     """
    #     try:
    #         # Nhận frames và convert sang base64
    #         base64_data = base64.b64encode(request.data).decode("ascii")
    #
    #         # Broadcast to frontend via WebSocket
    #         await socket_manage.broadcast_base64(base64_data)
    #
    #         logger.debug("Frame processed and broadcasted successfully")
    #         return frame_pb2.FrameResponse()
    #
    #     except Exception as e:
    #         logger.error(f"Error processing frame: {e}", exc_info=True)
    #         context.set_code(grpc.StatusCode.INTERNAL)
    #         context.set_details(f"Error processing frame: {str(e)}")
    #         return frame_pb2.FrameResponse()
