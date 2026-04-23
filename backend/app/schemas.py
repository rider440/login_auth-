from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ─── User Schemas ────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    name: str
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── OTP Schemas ─────────────────────────────────────────────────────────────

class SendOTPRequest(BaseModel):
    phone: str


class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str


class OTPResponse(BaseModel):
    message: str
    # In production, remove otp from response. Included here for dev/demo only.
    otp: Optional[str] = None


# ─── Token Schemas ────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    phone: Optional[str] = None
