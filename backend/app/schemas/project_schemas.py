from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    ProjectName: str
    Description: Optional[str] = None
    Status: Optional[str] = "Active"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    ProjectName: Optional[str] = None
    Description: Optional[str] = None
    Status: Optional[str] = None

class ProjectOut(ProjectBase):
    ProjectId: int
    company_id: int
    created_at: datetime

    class Config:
        from_attributes = True
