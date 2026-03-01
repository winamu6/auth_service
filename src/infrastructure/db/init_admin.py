import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from src.infrastructure.db.model.user_model import User, UserRole
from src.infrastructure.security import PasswordHelper
from src.infrastructure.config.settings import settings

async def create_admin():
    engine = create_async_engine(settings.DATABASE_URL_psycopg)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.login == settings.ADMIN_LOGIN))
        admin = result.scalar_one_or_none()

        if not admin:
            print(f"Создание администратора: {settings.ADMIN_LOGIN}")
            new_admin = User(
                login=settings.ADMIN_LOGIN,
                hashed_password=PasswordHelper.hash_password(settings.ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                branch=1,
                is_active=True
            )
            session.add(new_admin)
            await session.commit()
            print("Администратор успешно создан.")
        else:
            print("Администратор уже существует.")

if __name__ == "__main__":
    asyncio.run(create_admin())