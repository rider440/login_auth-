from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class EmployeeBase(BaseModel):
    FirstName: str
    LastName: str
    Email: EmailStr
    Phone: str
    is_active: Optional[bool] = True

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Email: Optional[EmailStr] = None
    Phone: Optional[str] = None
    is_active: Optional[bool] = None
        
class EmployeeOut(EmployeeBase):
    EmpId: int
    company_id: int
    created_at: datetime

    class Config:
        from_attributes = True
