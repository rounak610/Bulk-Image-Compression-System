from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://myusername:mypassword@localhost/image_processing"

engine = create_async_engine(DATABASE_URL, echo=True)

# Define the base class for all models
Base = declarative_base()

# Async session for database interaction
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session():
    async with async_session() as session:
        yield session
