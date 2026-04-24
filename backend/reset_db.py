from app.database import engine, Base
from app import models
from app.models.user_model import User
from app.models.Employee_model import Employee
from app.models.Task_model import task, task_assignee
from app.models.Otp_model import OTPStore

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("All tables dropped successfully.")
