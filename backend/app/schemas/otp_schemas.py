from pydantic import BaseModel, Field

class SendOTPRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=10)

class VerifyOTPRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=10)
    otp: str = Field(min_length=6, max_length=6)

class OTPResponse(BaseModel):
    message: str
    otp: str # For development logging only
