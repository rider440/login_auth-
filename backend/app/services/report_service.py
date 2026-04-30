from sqlalchemy.orm import Session, joinedload
from app.models.Assign_task_model import DailyReport
from app.models.Task_model import task
from app.models.Employee_model import Employee
from app.models.Project_model import Project
from app.models.Teams_model import Team
from app.schemas.task_schemas import DailyReportCreate

def create_report(db: Session, report: DailyReportCreate, emp_id: int, company_id: int):
    db_report = DailyReport(
        **report.model_dump(),
        emp_id=emp_id,
        company_id=company_id
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_reports(db: Session, company_id: int, emp_id: int = None, task_id: int = None):
    query = db.query(DailyReport).filter(DailyReport.company_id == company_id)
    
    if emp_id:
        query = query.filter(DailyReport.emp_id == emp_id)
    if task_id:
        query = query.filter(DailyReport.task_id == task_id)
    
    reports = query.order_by(DailyReport.created_at.desc()).all()
    
    # Manually populate the extra fields for the response model
    # (Or we could use a complex join in the query, but this is clearer for small datasets)
    for r in reports:
        # Task and related Project/Team
        db_task = db.query(task).filter(task.TaskId == r.task_id).first()
        if db_task:
            r.task_name = db_task.TaskName
            if db_task.project_id:
                db_project = db.query(Project).filter(Project.ProjectId == db_task.project_id).first()
                if db_project:
                    r.project_name = db_project.ProjectName
            if db_task.team_id:
                db_team = db.query(Team).filter(Team.TeamId == db_task.team_id).first()
                if db_team:
                    r.team_name = db_team.TeamName
        
        # Employee
        db_emp = db.query(Employee).filter(Employee.EmpId == r.emp_id).first()
        if db_emp:
            r.employee_name = f"{db_emp.FirstName} {db_emp.LastName}"
            
    return reports
