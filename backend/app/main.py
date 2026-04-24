from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base
from app import models, auth
from typing import List
from app.schemas import emp_schemas, task_schemas, user_schemas, otp_schemas, token_schemas
from app.services import emp_service, task_service, user_service, otp_service

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
    otp_service.save_otp(db, request.phone, otp)
    print(f"[DEV] OTP for {request.phone}: {otp}")
    return otp_schemas.OTPResponse(message="OTP sent successfully", otp=otp)


# ─── Verify OTP / Login (JSON Client) ─────────────────────────────────────────
@app.post("/verify-otp", response_model=token_schemas.Token)
def verify_otp(request: otp_schemas.VerifyOTPRequest, db: Session = Depends(get_db)):
    valid = otp_service.verify_otp(db, request.phone, request.otp)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP",
        )
    access_token = auth.create_access_token(data={"sub": request.phone})
    return token_schemas.Token(access_token=access_token, token_type="bearer")


# ─── Swagger UI Login (Form Data) ─────────────────────────────────────────────
@app.post("/token", response_model=token_schemas.Token, include_in_schema=False)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Swagger uses username/password form fields. We map username -> phone, password -> otp
    print(f"[DEV] /token received username: '{form_data.username}' password: '{form_data.password}'")
    valid = otp_service.verify_otp(db, form_data.username, form_data.password)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP",
        )
    access_token = auth.create_access_token(data={"sub": form_data.username})
    return token_schemas.Token(access_token=access_token, token_type="bearer")


# ─── Get Current User ─────────────────────────────────────────────────────────
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    phone = auth.decode_access_token(token)
    if not phone:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user = user_service.get_user_by_phone(db, phone)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@app.get("/me", response_model=user_schemas.UserResponse)
def get_me(current_user: user_schemas.UserResponse = Depends(get_current_user)):
    return current_user


# ─── Employees ────────────────────────────────────────────────────────────────

@app.post("/employees/", response_model=emp_schemas.EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(emp: emp_schemas.EmployeeCreate, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    return emp_service.create_employee(db, emp, current_user.company_id)

@app.get("/employees/", response_model=List[emp_schemas.EmployeeOut])
def read_employees(skip: int = 0, limit: int = 100, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    return emp_service.get_employees(db, current_user.company_id, skip=skip, limit=limit)

@app.get("/employees/{emp_id}", response_model=emp_schemas.EmployeeOut)
def read_employee(emp_id: int, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    db_emp = emp_service.get_employee(db, emp_id, current_user.company_id)
    if db_emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_emp

@app.put("/employees/{emp_id}", response_model=emp_schemas.EmployeeOut)
def update_employee(emp_id: int, emp: emp_schemas.EmployeeUpdate, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    db_emp = emp_service.update_employee(db, emp_id, emp, current_user.company_id)
    if db_emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_emp

@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: int, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    success = emp_service.delete_employee(db, emp_id, current_user.company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


# ─── Tasks ────────────────────────────────────────────────────────────────────

@app.post("/tasks/", response_model=task_schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task: task_schemas.TaskCreate, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    return task_service.create_task(db, task, current_user.company_id)

@app.get("/tasks/", response_model=List[task_schemas.TaskOut])
def read_tasks(skip: int = 0, limit: int = 100, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    return task_service.get_tasks(db, current_user.company_id, skip=skip, limit=limit)

@app.get("/tasks/{task_id}", response_model=task_schemas.TaskOut)
def read_task(task_id: int, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = task_service.get_task(db, task_id, current_user.company_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/tasks/{task_id}", response_model=task_schemas.TaskOut)
def update_task(task_id: int, task: task_schemas.TaskUpdate, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = task_service.update_task(db, task_id, task, current_user.company_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    success = task_service.delete_task(db, task_id, current_user.company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

# ─── Task Assignments ─────────────────────────────────────────────────────────

@app.post("/tasks/assign/", response_model=task_schemas.TaskAssigneeOut, status_code=status.HTTP_201_CREATED)
def assign_task(assign_data: task_schemas.TaskAssigneeCreate, current_user: user_schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    db_assignee = task_service.assign_task(db, assign_data, current_user.company_id)
    if not db_assignee:
        raise HTTPException(status_code=400, detail="Invalid task_id or emp_id for your company.")
    return db_assignee

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
