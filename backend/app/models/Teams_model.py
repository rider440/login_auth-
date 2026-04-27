from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

# Junction table for Team Members
team_members = Table(
    "team_members",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.TeamId", ondelete="CASCADE"), primary_key=True),
    Column("emp_id", Integer, ForeignKey("employees.EmpId", ondelete="CASCADE"), primary_key=True)
)

class Team(Base):
    __tablename__ = "teams"

    TeamId = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("users.company_id"), nullable=False)
    TeamName = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.ProjectId", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    members = relationship("Employee", secondary=team_members, backref="teams")
    project = relationship("Project", backref="teams")
