import random
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.Otp_model import OTPStore

def generate_otp() -> str:
    # Generate a 6-digit OTP
    return str(random.randint(100000, 999999))

def hash_otp(otp: str) -> str:
    # Use standard python sha256 to hash OTP without extra dependencies
    return hashlib.sha256(otp.encode('utf-8')).hexdigest()

def save_otp(db: Session, phone: str, otp: str):
    hashed_otp = hash_otp(otp)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    
    # Check if existing OTP for phone, update it, or create new
    db_otp = db.query(OTPStore).filter(OTPStore.phone == phone).first()
    if db_otp:
        db_otp.otp = hashed_otp
        db_otp.expires_at = expires_at
        db_otp.created_at = datetime.now(timezone.utc)
    else:
        db_otp = OTPStore(
            phone=phone,
            otp=hashed_otp,
            expires_at=expires_at
        )
        db.add(db_otp)
    
    db.commit()
    return db_otp

def verify_otp(db: Session, phone: str, otp: str) -> bool:
    hashed_otp = hash_otp(otp)
    db_otp = db.query(OTPStore).filter(OTPStore.phone == phone).first()
    
    if not db_otp:
        return False
        
    # Check expiry
    if datetime.now(timezone.utc) > db_otp.expires_at:
        return False
        
    # Check if hash matches
    if db_otp.otp != hashed_otp:
        return False
        
    # Valid OTP, we can delete it so it can't be reused
    db.delete(db_otp)
    db.commit()
    return True
