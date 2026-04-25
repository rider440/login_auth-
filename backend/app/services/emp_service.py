from sqlalchemy.orm import Session
import random
import string
from app.models.Employee_model import Employee
from app.schemas.emp_schemas import EmployeeCreate, EmployeeUpdate

def create_employee(db: Session, emp: EmployeeCreate, company_id: int):
    login_code = "Emp" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    while db.query(Employee).filter(Employee.Login_Code == login_code).first():
        login_code = "Emp" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

    db_emp = Employee(**emp.model_dump(), company_id=company_id, Login_Code=login_code)
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

def get_employees(db: Session, company_id: int, skip: int = 0, limit: int = 100):
    return db.query(Employee).filter(Employee.company_id == company_id).offset(skip).limit(limit).all()

def get_employee(db: Session, emp_id: int, company_id: int):
    return db.query(Employee).filter(Employee.EmpId == emp_id, Employee.company_id == company_id).first()

def update_employee(db: Session, emp_id: int, emp: EmployeeUpdate, company_id: int):
    db_emp = get_employee(db, emp_id, company_id)
    if not db_emp:
        return None
    
    update_data = emp.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_emp, key, value)
        
    db.commit()
    db.refresh(db_emp)
    return db_emp

def delete_employee(db: Session, emp_id: int, company_id: int):
    db_emp = get_employee(db, emp_id, company_id)
    if not db_emp:
        return False
    db.delete(db_emp)
    db.commit()
    return True
