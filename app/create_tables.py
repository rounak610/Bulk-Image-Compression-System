from app.database import engine, Base

def create_tables():
    with engine.begin() as conn:
        Base.metadata.create_all(conn)

if __name__ == "__main__":
    create_tables()
