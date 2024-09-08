from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://myusername:mypassword@localhost/image_processing"

engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(
    bind=engine, expire_on_commit=False
)

def get_session():
    return SessionLocal()
