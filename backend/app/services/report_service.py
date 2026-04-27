from sqlalchemy.orm import Session
from app.models.Assign_task_model import DailyReport
from app.schemas.task_schemas import DailyReportCreate

def create_report(db: Session, report: DailyReportCreate, emp_id: int, company_id: int):
    db_report = DailyReport(
        **report.model_dump(),
        emp_id=emp_id,
        company_id=company_id
    )
    db.add(db_report)
    
    # Also update the task status in the task table
    from app.models.Task_model import task
    db_task = db.query(task).filter(task.TaskId == report.task_id, task.company_id == company_id).first()
    if db_task:
        db_task.status = report.Status
        
    db.commit()
    db.refresh(db_report)
    return db_report

def get_reports(db: Session, company_id: int, emp_id: int = None, task_id: int = None):
    query = db.query(DailyReport).filter(DailyReport.company_id == company_id)
    if emp_id:
        query = query.filter(DailyReport.emp_id == emp_id)
    if task_id:
        query = query.filter(DailyReport.task_id == task_id)
    return query.order_by(DailyReport.created_at.desc()).all()
