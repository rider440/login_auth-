from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    TaskName: str
    description: Optional[str] = None
    status: Optional[str] = "Pending"
    priority: Optional[str] = "Normal"
    is_active: Optional[bool] = True

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    TaskName: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    is_active: Optional[bool] = None

class TaskOut(TaskBase):
    TaskId: int
    company_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TaskAssigneeBase(BaseModel):
    task_id: int
    emp_id: int
    status: Optional[str] = "Pending"
    is_active: Optional[bool] = True

class TaskAssigneeCreate(TaskAssigneeBase):
    pass

class TaskAssigneeUpdate(BaseModel):
    status: Optional[str] = None
    is_active: Optional[bool] = None

class TaskAssigneeOut(TaskAssigneeBase):
    TaskAssigneeId: int
    created_at: datetime

    class Config:
        from_attributes = True

class TaskBulkAssign(BaseModel):
    task_id: int
    emp_ids: list[int]
