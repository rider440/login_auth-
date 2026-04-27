from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base
from app import models, auth
from typing import List
from app.schemas import emp_schemas, task_schemas, user_schemas, otp_schemas, token_schemas, project_schemas, team_schemas
from app.services import emp_service, task_service, user_service, otp_service, project_service, team_service, report_service

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Login API", version="1.0.0")

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# ─── OAuth2 Scheme ────────────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Login API is running"}


# ─── Register ─────────────────────────────────────────────────────────────────
@app.post("/register", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    existing = user_service.get_user_by_phone(db, user.phone)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered",
        )
    return user_service.create_user(db, user)


# ─── Send OTP ─────────────────────────────────────────────────────────────────
@app.post("/send-otp", response_model=otp_schemas.OTPResponse)
def send_otp(request: otp_schemas.SendOTPRequest, db: Session = Depends(get_db)):
    user = user_service.get_user_by_phone(db, request.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not registered. Please register first.",
        )
    otp = otp_service.generate_otp()
    result = otp_service.save_otp(db, request.phone, otp)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Too many attempts. Your account is blocked for 24 hours.",
        )
    print(f"[DEV] OTP for {request.phone}: {otp}")
    return otp_schemas.OTPResponse(message="OTP sent successfully", otp=otp)


# ─── Verify OTP / Login (JSON Client) ─────────────────────────────────────────
@app.post("/verify-otp", response_model=token_schemas.Token)
def verify_otp(request: otp_schemas.VerifyOTPRequest, db: Session = Depends(get_db)):
    result = otp_service.verify_otp(db, request.phone, request.otp)
    if not result["success"]:
        status_code = status.HTTP_403_FORBIDDEN if result["is_blocked"] else status.HTTP_401_UNAUTHORIZED
        raise HTTPException(
            status_code=status_code,
            detail=result["message"],
        )
    access_token = auth.create_access_token(data={"sub": request.phone})
    return token_schemas.Token(access_token=access_token, token_type="bearer")


# ─── Swagger UI Login (Form Data) ─────────────────────────────────────────────
@app.post("/token", response_model=token_schemas.Token, include_in_schema=False)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Swagger uses username/password form fields. We map username -> phone, password -> otp
    print(f"[DEV] /token received username: '{form_data.username}' password: '{form_data.password}'")
    result = otp_service.verify_otp(db, form_data.username, form_data.password)
    if not result["success"]:
        status_code = status.HTTP_403_FORBIDDEN if result["is_blocked"] else status.HTTP_401_UNAUTHORIZED
        raise HTTPException(
            status_code=status_code,
            detail=result["message"],
        )
    access_token = auth.create_access_token(data={"sub": form_data.username})
    return token_schemas.Token(access_token=access_token, token_type="bearer")


from app.schemas import auth_schemas

# ─── Auth ─────────────────────────────────────────────────────────────────────

@app.post("/auth/check-phone", response_model=auth_schemas.PhoneCheckResponse)
def check_phone(request: auth_schemas.PhoneCheckRequest, db: Session = Depends(get_db)):
    user = user_service.get_user_by_phone(db, request.phone)
    if user:
        return auth_schemas.PhoneCheckResponse(exists=True, user_type="admin")
    
    employee = emp_service.get_employee_by_phone(db, request.phone)
    if employee:
        return auth_schemas.PhoneCheckResponse(exists=True, user_type="employee")
    
    return auth_schemas.PhoneCheckResponse(exists=False, user_type="none")

@app.post("/auth/employee-login", response_model=token_schemas.Token)
def employee_login(request: auth_schemas.EmployeeLoginRequest, db: Session = Depends(get_db)):
    employee = emp_service.verify_employee_login(db, request.phone, request.login_code)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Login Code",
        )
    access_token = auth.create_access_token(data={"sub": request.phone, "role": "employee"})
    return token_schemas.Token(access_token=access_token, token_type="bearer")


# ─── Get Current User ─────────────────────────────────────────────────────────
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    phone = payload.get("sub")
    role = payload.get("role", "admin") # Default to admin for backward compatibility
    
    if role == "employee":
        employee = emp_service.get_employee_by_phone(db, phone)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        # Add a dynamic 'role' attribute for easy checking
        employee.role = "employee"
        return employee
    else:
        user = user_service.get_user_by_phone(db, phone)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.role = "admin"
        return user

@app.get("/me")
def get_me(current_user = Depends(get_current_user)):
    if current_user.role == "employee":
        return {
            "id": current_user.EmpId,
            "name": f"{current_user.FirstName} {current_user.LastName}",
            "phone": current_user.Phone,
            "company_id": current_user.company_id,
            "role": "employee",
            "login_code": current_user.Login_Code
        }
    return {
        "id": current_user.company_id,
        "name": current_user.name,
        "phone": current_user.phone,
        "company_id": current_user.company_id,
        "role": "admin"
    }

def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can perform this action")
    return current_user


# ─── Employees ────────────────────────────────────────────────────────────────

@app.post("/employees/", response_model=emp_schemas.EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(emp: emp_schemas.EmployeeCreate, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    return emp_service.create_employee(db, emp, current_user.company_id)

@app.get("/employees/", response_model=List[emp_schemas.EmployeeOut])
def read_employees(skip: int = 0, limit: int = 100, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Employees should only see their own profile or nothing here?
    # For now, let's restrict listing all employees to admin
    if current_user.role != "admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can list all employees")
    return emp_service.get_employees(db, current_user.company_id, skip=skip, limit=limit)

@app.get("/employees/{emp_id}", response_model=emp_schemas.EmployeeOut)
def read_employee(emp_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Employees can only read their own profile
    if current_user.role == "employee" and current_user.EmpId != emp_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    db_emp = emp_service.get_employee(db, emp_id, current_user.company_id)
    if db_emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_emp

@app.put("/employees/{emp_id}", response_model=emp_schemas.EmployeeOut)
def update_employee(emp_id: int, emp: emp_schemas.EmployeeUpdate, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    db_emp = emp_service.update_employee(db, emp_id, emp, current_user.company_id)
    if db_emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_emp

@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: int, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    success = emp_service.delete_employee(db, emp_id, current_user.company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


# ─── Tasks ────────────────────────────────────────────────────────────────────

@app.post("/tasks/", response_model=task_schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task: task_schemas.TaskCreate, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    return task_service.create_task(db, task, current_user.company_id)

@app.get("/tasks/", response_model=List[task_schemas.TaskOut])
def read_tasks(project_id: int = None, team_id: int = None, skip: int = 0, limit: int = 100, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "employee":
        # Employees only see tasks assigned to them
        return task_service.get_tasks_by_employee(db, current_user.EmpId, current_user.company_id)
    return task_service.get_tasks(db, current_user.company_id, project_id=project_id, team_id=team_id, skip=skip, limit=limit)

@app.get("/tasks/{task_id}", response_model=task_schemas.TaskOut)
def read_task(task_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = task_service.get_task(db, task_id, current_user.company_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if current_user.role == "employee":
        # Check if task is assigned to this employee
        assignments = task_service.get_task_assignments(db, task_id, current_user.company_id)
        if not any(a.emp_id == current_user.EmpId for a in assignments):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            
    return db_task

@app.put("/tasks/{task_id}", response_model=task_schemas.TaskOut)
def update_task(task_id: int, task: task_schemas.TaskUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "employee":
        # Employees can ONLY change status of their own tasks
        assignments = task_service.get_task_assignments(db, task_id, current_user.company_id)
        if not any(a.emp_id == current_user.EmpId for a in assignments):
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        # Only allow status update
        task_data = task.model_dump(exclude_unset=True)
        if any(key != "status" for key in task_data.keys()):
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employees can only update task status")

    db_task = task_service.update_task(db, task_id, task, current_user.company_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    success = task_service.delete_task(db, task_id, current_user.company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

# ─── Task Assignments ─────────────────────────────────────────────────────────

@app.post("/tasks/assign/", response_model=task_schemas.TaskAssigneeOut, status_code=status.HTTP_201_CREATED)
def assign_task(assign_data: task_schemas.TaskAssigneeCreate, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    db_assignee = task_service.assign_task(db, assign_data, current_user.company_id)
    if not db_assignee:
        raise HTTPException(status_code=400, detail="Invalid task_id or emp_id for your company.")
    return db_assignee

@app.post("/tasks/bulk-assign/", status_code=status.HTTP_200_OK)
def bulk_assign_task(assign_data: task_schemas.TaskBulkAssign, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    success = task_service.bulk_assign_task(db, assign_data, current_user.company_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to assign tasks. Verify task and employee IDs.")
    return {"message": "Tasks assigned successfully"}

@app.get("/tasks/{task_id}/assignments", response_model=List[task_schemas.TaskAssigneeOut])
def get_task_assignments(task_id: int, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    return task_service.get_task_assignments(db, task_id, current_user.company_id)

@app.put("/tasks/assignments/{assignment_id}", response_model=task_schemas.TaskAssigneeOut)
def update_task_assignment(assignment_id: int, update_data: task_schemas.TaskAssigneeUpdate, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    db_assignee = task_service.update_task_assignment(db, assignment_id, update_data, current_user.company_id)
    if db_assignee is None:
        raise HTTPException(status_code=404, detail="Task assignment not found")
    return db_assignee

@app.delete("/tasks/assignments/{assignment_id}")
def delete_task_assignment(assignment_id: int, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    success = task_service.delete_task_assignment(db, assignment_id, current_user.company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task assignment not found")
    return {"message": "Task assignment deleted successfully"}


# ─── Projects ─────────────────────────────────────────────────────────────────

@app.post("/projects/", response_model=project_schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(project: project_schemas.ProjectCreate, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    return project_service.create_project(db, project, current_user.company_id)

@app.get("/projects/", response_model=List[project_schemas.ProjectOut])
def read_projects(skip: int = 0, limit: int = 100, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return project_service.get_projects(db, current_user.company_id, skip=skip, limit=limit)

@app.get("/projects/{project_id}", response_model=project_schemas.ProjectOut)
def read_project(project_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_project = project_service.get_project(db, project_id, current_user.company_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.put("/projects/{project_id}", response_model=project_schemas.ProjectOut)
def update_project(project_id: int, project: project_schemas.ProjectUpdate, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    db_project = project_service.update_project(db, project_id, project, current_user.company_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    success = project_service.delete_project(db, project_id, current_user.company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}


# ─── Teams ────────────────────────────────────────────────────────────────────

@app.post("/teams/", response_model=team_schemas.TeamOut, status_code=status.HTTP_201_CREATED)
def create_team(team: team_schemas.TeamCreate, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    return team_service.create_team(db, team, current_user.company_id)

@app.get("/teams/", response_model=List[team_schemas.TeamOut])
def read_teams(project_id: int = None, skip: int = 0, limit: int = 100, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return team_service.get_teams(db, current_user.company_id, project_id=project_id, skip=skip, limit=limit)

@app.get("/teams/{team_id}", response_model=team_schemas.TeamOut)
def read_team(team_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_team = team_service.get_team(db, team_id, current_user.company_id)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team

@app.put("/teams/{team_id}", response_model=team_schemas.TeamOut)
def update_team(team_id: int, team: team_schemas.TeamUpdate, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    db_team = team_service.update_team(db, team_id, team, current_user.company_id)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team

@app.delete("/teams/{team_id}")
def delete_team(team_id: int, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    success = team_service.delete_team(db, team_id, current_user.company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"message": "Team deleted successfully"}


# ─── Daily Reports ────────────────────────────────────────────────────────────

@app.post("/reports/", response_model=task_schemas.DailyReportOut, status_code=status.HTTP_201_CREATED)
def create_report(report: task_schemas.DailyReportCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "employee":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only employees can create daily reports")
    return report_service.create_report(db, report, current_user.EmpId, current_user.company_id)

@app.get("/reports/", response_model=List[task_schemas.DailyReportOut])
def read_reports(emp_id: int = None, task_id: int = None, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Employees can only see their own reports
    if current_user.role == "employee":
        emp_id = current_user.EmpId
    return report_service.get_reports(db, current_user.company_id, emp_id=emp_id, task_id=task_id)
