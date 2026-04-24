from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    phone: str = Field(min_length=10, max_length=10)
    address: Optional[str] = None
    city: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    company_id: int
    created_at: datetime

    class Config:
        from_attributes = True
