from sqlalchemy.orm import Session
from app.models.Task_model import task, task_assignee
from app.models.Employee_model import Employee
from app.schemas.task_schemas import TaskCreate, TaskUpdate, TaskAssigneeCreate, TaskAssigneeUpdate, TaskBulkAssign

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

def bulk_assign_task(db: Session, assign_data: TaskBulkAssign, company_id: int):
    # Verify task belongs to company
    db_task = get_task(db, assign_data.task_id, company_id)
    if not db_task:
        return None
    
    # Filter valid employee IDs (must belong to the company)
    valid_emp_ids = [
        e[0] for e in db.query(Employee.EmpId).filter(
            Employee.EmpId.in_(assign_data.emp_ids),
            Employee.company_id == company_id
        ).all()
    ]
    
    # Remove existing assignments that are NOT in the new valid list
    db.query(task_assignee).filter(
        task_assignee.task_id == assign_data.task_id,
        ~task_assignee.emp_id.in_(valid_emp_ids)
    ).delete(synchronize_session=False)
    
    # Get currently assigned IDs after deletion to avoid duplicates
    remaining_assignments = db.query(task_assignee.emp_id).filter(task_assignee.task_id == assign_data.task_id).all()
    current_emp_ids = {a[0] for a in remaining_assignments}
    
    # Add new assignments
    for emp_id in valid_emp_ids:
        if emp_id not in current_emp_ids:
            new_assignee = task_assignee(task_id=assign_data.task_id, emp_id=emp_id)
            db.add(new_assignee)
    
    db.commit()
    return True

def get_tasks_by_employee(db: Session, emp_id: int, company_id: int):
    # Get task IDs assigned to the employee
    task_ids = db.query(task_assignee.task_id).filter(task_assignee.emp_id == emp_id).all()
    task_ids = [tid[0] for tid in task_ids]
    
    # Return those tasks belonging to the same company
    return db.query(task).filter(task.TaskId.in_(task_ids), task.company_id == company_id).all()
