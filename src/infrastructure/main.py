import asyncio
from concurrent import futures

import grpc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.infrastructure.repository import SQLAlchemyUserRepository
from src.application.services.user_services import UserService
from src.application.services.auth_service import AuthService
from src.api.grpc_server import AuthServicer
from src.infrastructure.grpc import auth_pb2_grpc
from src.infrastructure.config.settings import settings


async def serve():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))

    async with async_session() as session:
        user_repo = SQLAlchemyUserRepository(session)
        user_service = UserService(user_repo)
        auth_service = AuthService(user_repo)

        auth_pb2_grpc.add_AuthNavigationServicer_to_server(
            AuthServicer(auth_service, user_service), server
        )

        listen_addr = "[::]:50051"
        server.add_insecure_port(listen_addr)
        print(f"gRPC сервер запущен на {listen_addr}")

        await server.start()
        await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())