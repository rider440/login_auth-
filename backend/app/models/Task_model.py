from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, UniqueConstraint
from app.database import Base

class task(Base):
    __tablename__ = "tasks"
    __table_args__ = (UniqueConstraint('company_id', 'TaskName', name='uq_task_company_TaskName'),)


    TaskId = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("users.company_id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.ProjectId", ondelete="CASCADE"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.TeamId", ondelete="SET NULL"), nullable=True)
    TaskName = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=True, default="Pending")
    priority = Column(String, nullable=True, default="Normal")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class task_assignee(Base):
    __tablename__ = "task_assignee"
    __table_args__ = (UniqueConstraint('task_id', 'emp_id', name='uq_task_assignee_task_id_emp_id'),)


    TaskAssigneeId = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.TaskId", ondelete="CASCADE"), nullable=False)
    emp_id = Column(Integer, ForeignKey("employees.EmpId", ondelete="CASCADE"), nullable=False)  
    status = Column(String, nullable=True, default="Pending")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())