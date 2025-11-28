import asyncio
import grpc
from app.modules.clarius.proto import frame_pb2_grpc, frame_pb2


async def run():
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = frame_pb2_grpc.FrameServiceStub(channel)
        print("Sending frame to gRPC server...")
        response = await stub.SendFrame(frame_pb2.FrameRequest(data=b'dummy_image_data'))
        print("Frame sent successfully.")

if __name__ == '__main__':
    asyncio.run(run())
