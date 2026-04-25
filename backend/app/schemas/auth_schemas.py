from pydantic import BaseModel, Field
from typing import Literal

class PhoneCheckRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=10)

class PhoneCheckResponse(BaseModel):
    exists: bool
    user_type: Literal["admin", "employee", "none"]

class EmployeeLoginRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=10)
    login_code: str
