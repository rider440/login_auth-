import random
import string
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app import models
from app import schemas


def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        name=user.name,
        phone=user.phone,
        address=user.address,
        city=user.city,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def save_otp(db: Session, phone: str, otp: str):
    # Invalidate old OTPs for this phone
    db.query(models.OTPStore).filter(
        models.OTPStore.phone == phone,
        models.OTPStore.is_used == False,
    ).update({"is_used": True})
    db.commit()

    db_otp = models.OTPStore(phone=phone, otp=otp)
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)
    return db_otp


def verify_otp(db: Session, phone: str, otp: str) -> bool:
    record = (
        db.query(models.OTPStore)
        .filter(
            models.OTPStore.phone == phone,
            models.OTPStore.otp == otp,
            models.OTPStore.is_used == False,
        )
        .order_by(models.OTPStore.created_at.desc())
        .first()
    )
    if not record:
        return False

    # Mark as used to prevent replay attacks
    record.is_used = True
    db.commit()

    # Check if expired (5 minutes)
    now = datetime.now(timezone.utc)
    if now - record.created_at > timedelta(minutes=5):
        return False

    return True
