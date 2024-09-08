from app.database import engine, Base
from app.models import Product  # Import your Product model

def create_tables():
    with engine.begin() as conn:
        Base.metadata.create_all(conn)

if __name__ == "__main__":
    create_tables()
