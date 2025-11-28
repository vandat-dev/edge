import logging
from contextlib import asynccontextmanager
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from app.core.setting import settings
from app.modules.user.model import Base  # ensure models are loaded

# Global variables
async_engine = None
AsyncSessionLocal = None

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    global async_engine, AsyncSessionLocal

    try:
        # Create async engine for SQLite
        database_url = settings.database_url
        # Ensure the directory exists
        db_path = database_url.replace("sqlite+aiosqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        async_engine = create_async_engine(
            database_url,
            echo=False,
            connect_args={"check_same_thread": False},  # Required for SQLite
        )

        # Create tables if they do not exist
        # async with async_engine.begin() as conn:
        #     await conn.run_sync(Base.metadata.create_all)

        # Test database connection
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        # Create session factory
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("✅ Database connected successfully.")

    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        logger.warning("⚠️  Continuing startup without active DB connection...")
        async_engine = None
        AsyncSessionLocal = None

    yield

    if async_engine:
        await async_engine.dispose()


async def get_session() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
