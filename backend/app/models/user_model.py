from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    company_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String(10), unique=True, index=True, nullable=False)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
