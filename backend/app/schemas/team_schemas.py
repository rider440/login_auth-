from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.emp_schemas import EmployeeOut

class TeamBase(BaseModel):
    TeamName: str
    project_id: int

class TeamCreate(TeamBase):
    member_ids: List[int] = []

class TeamUpdate(BaseModel):
    TeamName: Optional[str] = None
    project_id: Optional[int] = None
    member_ids: Optional[List[int]] = None

class TeamOut(TeamBase):
    TeamId: int
    company_id: int
    created_at: datetime
    members: List[EmployeeOut] = []

    class Config:
        from_attributes = True
