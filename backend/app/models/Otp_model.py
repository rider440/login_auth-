from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class OTPStore(Base):
    __tablename__ = "otp_store"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(10), index=True, nullable=False)
    otp = Column(String, nullable=False) # Hashed OTP
    attempts = Column(Integer, default=0)
    blocked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
