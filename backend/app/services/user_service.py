import random
from sqlalchemy.orm import Session
from app.models.user_model import User
from app.schemas.user_schemas import UserCreate

def get_user_by_phone(db: Session, phone: str):
    return db.query(User).filter(User.phone == phone).first()

def create_user(db: Session, user: UserCreate):
    # Generate unique 6 digit company_id
    company_id = random.randint(100000, 999999)
    while db.query(User).filter(User.company_id == company_id).first():
        company_id = random.randint(100000, 999999)
        
    db_user = User(
        company_id=company_id,
        name=user.name,
        phone=user.phone,
        address=user.address,
        city=user.city
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
