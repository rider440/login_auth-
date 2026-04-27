from sqlalchemy.orm import Session
from app.models.Project_model import Project
from app.schemas.project_schemas import ProjectCreate, ProjectUpdate

def create_project(db: Session, project: ProjectCreate, company_id: int):
    db_project = Project(**project.model_dump(), company_id=company_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects(db: Session, company_id: int, skip: int = 0, limit: int = 100):
    return db.query(Project).filter(Project.company_id == company_id, Project.is_active == True).offset(skip).limit(limit).all()

def get_project(db: Session, project_id: int, company_id: int):
    return db.query(Project).filter(Project.ProjectId == project_id, Project.company_id == company_id).first()

def update_project(db: Session, project_id: int, project: ProjectUpdate, company_id: int):
    db_project = get_project(db, project_id, company_id)
    if not db_project:
        return None
    
    update_data = project.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int, company_id: int):
    db_project = get_project(db, project_id, company_id)
    if not db_project:
        return False
    
    db_project.is_active = False
    db.commit()
    return True
