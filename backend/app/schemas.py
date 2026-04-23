from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─── User Schemas ────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    name: str
    phone: str = Field(..., min_length=10, max_length=10, pattern=r"^\d{10}$")
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
    phone: str = Field(..., min_length=10, max_length=10, pattern=r"^\d{10}$")


class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=10, pattern=r"^\d{10}$")
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


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
