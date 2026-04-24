from sqlalchemy.orm import Session
from app.models.Task_model import task, task_assignee
from app.models.Employee_model import Employee
from app.schemas.task_schemas import TaskCreate, TaskUpdate, TaskAssigneeCreate, TaskAssigneeUpdate

def create_task(db: Session, task_data: TaskCreate, company_id: int):
    db_task = task(**task_data.model_dump(), company_id=company_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, company_id: int, skip: int = 0, limit: int = 100):
    return db.query(task).filter(task.company_id == company_id).offset(skip).limit(limit).all()

def get_task(db: Session, task_id: int, company_id: int):
    return db.query(task).filter(task.TaskId == task_id, task.company_id == company_id).first()

def update_task(db: Session, task_id: int, task_data: TaskUpdate, company_id: int):
    db_task = get_task(db, task_id, company_id)
    if not db_task:
        return None
    
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
        
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int, company_id: int):
    db_task = get_task(db, task_id, company_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True

# Task Assignee operations
def assign_task(db: Session, assignee_data: TaskAssigneeCreate, company_id: int):
    # Verify task belongs to company
    db_task = get_task(db, assignee_data.task_id, company_id)
    if not db_task:
        return None
    
    # Verify employee belongs to company
    db_emp = db.query(Employee).filter(Employee.EmpId == assignee_data.emp_id, Employee.company_id == company_id).first()
    if not db_emp:
        return None

    db_assignee = task_assignee(**assignee_data.model_dump())
    db.add(db_assignee)
    db.commit()
    db.refresh(db_assignee)
    return db_assignee

def get_task_assignments(db: Session, task_id: int, company_id: int):
    db_task = get_task(db, task_id, company_id)
    if not db_task:
        return []
    return db.query(task_assignee).filter(task_assignee.task_id == task_id).all()

def update_task_assignment(db: Session, assignment_id: int, update_data: TaskAssigneeUpdate, company_id: int):
    db_assignee = db.query(task_assignee).filter(task_assignee.TaskAssigneeId == assignment_id).first()
    if not db_assignee:
        return None
    
    # Ensure task belongs to company
    db_task = get_task(db, db_assignee.task_id, company_id)
    if not db_task:
        return None
        
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_assignee, key, value)
        
    db.commit()
    db.refresh(db_assignee)
    return db_assignee

def delete_task_assignment(db: Session, assignment_id: int, company_id: int):
    db_assignee = db.query(task_assignee).filter(task_assignee.TaskAssigneeId == assignment_id).first()
    if not db_assignee:
        return False
        
    db_task = get_task(db, db_assignee.task_id, company_id)
    if not db_task:
        return False
        
    db.delete(db_assignee)
    db.commit()
    return True
