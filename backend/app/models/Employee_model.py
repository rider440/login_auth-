from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"

    EmpId = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("users.company_id"), nullable=False)
    FirstName = Column(String, nullable=False)
    LastName = Column(String, nullable=False)
    Email = Column(String, unique=True, index=True, nullable=False)
    Phone = Column(String(10), unique=True, index=True, nullable=False)
    Login_Code = Column(String, unique=True, index=True)
    Role = Column(String, default="employee") # admin, employee
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
