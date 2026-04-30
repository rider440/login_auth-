from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class DailyReport(Base):
    __tablename__ = "daily_reports"

    ReportId = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("users.company_id"), nullable=False)
    emp_id = Column(Integer, ForeignKey("employees.EmpId", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.TaskId", ondelete="CASCADE"), nullable=False)
    ReportDate = Column(DateTime(timezone=True), server_default=func.now())
    UpdateContent = Column(String, nullable=False)
    Status = Column(String, nullable=False) # Status updated at time of report
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("task", backref="reports")
    employee = relationship("Employee", backref="reports")
