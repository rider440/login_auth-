from sqlalchemy.orm import Session
from app.models.Teams_model import Team
from app.models.Employee_model import Employee
from app.schemas.team_schemas import TeamCreate, TeamUpdate

def create_team(db: Session, team: TeamCreate, company_id: int):
    # Extract member_ids
    member_ids = team.member_ids
    team_data = team.model_dump(exclude={"member_ids"})
    
    db_team = Team(**team_data, company_id=company_id)
    
    # Add members
    if member_ids:
        employees = db.query(Employee).filter(Employee.EmpId.in_(member_ids), Employee.company_id == company_id).all()
        db_team.members = employees
        
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

def get_teams(db: Session, company_id: int, project_id: int = None, skip: int = 0, limit: int = 100):
    query = db.query(Team).filter(Team.company_id == company_id, Team.is_active == True)
    if project_id:
        query = query.filter(Team.project_id == project_id)
    return query.offset(skip).limit(limit).all()

def get_team(db: Session, team_id: int, company_id: int):
    return db.query(Team).filter(Team.TeamId == team_id, Team.company_id == company_id).first()

def update_team(db: Session, team_id: int, team: TeamUpdate, company_id: int):
    db_team = get_team(db, team_id, company_id)
    if not db_team:
        return None
    
    update_data = team.model_dump(exclude_unset=True, exclude={"member_ids"})
    for key, value in update_data.items():
        setattr(db_team, key, value)
    
    if team.member_ids is not None:
        employees = db.query(Employee).filter(Employee.EmpId.in_(team.member_ids), Employee.company_id == company_id).all()
        db_team.members = employees
        
    db.commit()
    db.refresh(db_team)
    return db_team

def delete_team(db: Session, team_id: int, company_id: int):
    db_team = get_team(db, team_id, company_id)
    if not db_team:
        return False
    
    db_team.is_active = False
    db.commit()
    return True
