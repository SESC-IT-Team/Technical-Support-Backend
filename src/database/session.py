from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session