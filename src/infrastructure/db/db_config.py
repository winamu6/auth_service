import asyncio
import logging
import asyncpg

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL_asyncpg

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    echo=False
)

Base = declarative_base()

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def wait_for_db():
    max_attempts = 60

    logger.info("Starting database readiness check...")

    for i in range(max_attempts):
        try:
            conn = await asyncpg.connect(
                user=settings.DB_USER,
                password=settings.DB_PASS,
                database=settings.DB_NAME,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
            )
            await conn.close()

            logger.info("Database is ready and connection established.")
            return

        except Exception as e:
            logger.warning(
                f"Waiting for database ({i + 1}/{max_attempts})... Error: {e.__class__.__name__}: {e}"
            )
            await asyncio.sleep(1)

    logger.critical("Database not ready after maximum attempts. Shutting down.")
    raise RuntimeError("Database not ready after 60 seconds")


async def init_db_and_create_tables():
    logger.info("Checking database schema...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables verified/created.")