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
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=5)
    
    # Check if existing OTP for phone
    db_otp = db.query(OTPStore).filter(OTPStore.phone == phone).first()
    
    if db_otp:
        # Check if user is blocked
        if db_otp.blocked_until and now < db_otp.blocked_until:
            # Still blocked
            return None
            
        # If block expired, reset attempts
        if db_otp.blocked_until and now >= db_otp.blocked_until:
            db_otp.attempts = 0
            db_otp.blocked_until = None
            
        db_otp.otp = hashed_otp
        db_otp.expires_at = expires_at
        db_otp.created_at = now
    else:
        db_otp = OTPStore(
            phone=phone,
            otp=hashed_otp,
            expires_at=expires_at,
            attempts=0
        )
        db.add(db_otp)
    
    db.commit()
    return db_otp

def verify_otp(db: Session, phone: str, otp: str) -> dict:
    """
    Returns a dict with:
    - success: bool
    - message: Optional[str]
    - is_blocked: bool
    """
    now = datetime.now(timezone.utc)
    db_otp = db.query(OTPStore).filter(OTPStore.phone == phone).first()
    
    if not db_otp:
        return {"success": False, "message": "OTP not found", "is_blocked": False}
        
    # Check if currently blocked
    if db_otp.blocked_until and now < db_otp.blocked_until:
        return {"success": False, "message": "Too many attempts. Please try after 24 hours.", "is_blocked": True}

    # Check expiry
    if now > db_otp.expires_at:
        return {"success": False, "message": "OTP expired", "is_blocked": False}
        
    # Check if hash matches
    hashed_otp = hash_otp(otp)
    if db_otp.otp != hashed_otp:
        # Increment attempts
        db_otp.attempts += 1
        if db_otp.attempts >= 3:
            db_otp.blocked_until = now + timedelta(days=1)
            db.commit()
            return {"success": False, "message": "Too many attempts. You are blocked for 24 hours.", "is_blocked": True}
        
        db.commit()
        remaining = 3 - db_otp.attempts
        return {"success": False, "message": f"Invalid OTP. {remaining} attempts remaining.", "is_blocked": False}
        
    # Valid OTP, we can reset attempts and delete/invalidate current OTP
    # We'll just delete the record or reset it.
    # To keep the 'attempts' history for the 24h block, we should probably reset attempts to 0 here.
    db_otp.attempts = 0
    db_otp.blocked_until = None
    db.delete(db_otp)
    db.commit()
    return {"success": True, "message": "OTP verified", "is_blocked": False}
