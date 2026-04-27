from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    ProjectId = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("users.company_id"), nullable=False)
    ProjectName = Column(String, nullable=False)
    Description = Column(String, nullable=True)
    Status = Column(String, default="Active") # Active, Completed, On Hold
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
