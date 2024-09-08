from sqlalchemy import Column, Integer, String
from app.database import Base

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    input_image_url = Column(String)
    output_image_url = Column(String, nullable=True)
    status = Column(String, default="Pending")
    request_id = Column(String, index=True, nullable=True)
