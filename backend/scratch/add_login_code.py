import os
import random
import string
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load database configuration
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def generate_login_code():
    return "Emp" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

def migrate():
    with engine.connect() as conn:
        print("Checking if 'Login_Code' column exists...")
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='employees' AND column_name='Login_Code';
        """))
        if result.fetchone():
            print("Column 'Login_Code' already exists. Skipping.")
            return

        print("Step 1: Adding 'Login_Code' column (nullable)...")
        conn.execute(text('ALTER TABLE employees ADD COLUMN "Login_Code" VARCHAR;'))
        conn.commit()

        print("Step 2: Generating unique codes for existing employees...")
        employees = conn.execute(text('SELECT "EmpId" FROM employees')).fetchall()
        for emp in employees:
            emp_id = emp[0]
            code = generate_login_code()
            print(f"Assigning {code} to Employee ID {emp_id}")
            conn.execute(
                text('UPDATE employees SET "Login_Code" = :code WHERE "EmpId" = :id'),
                {"code": code, "id": emp_id}
            )
        conn.commit()

        print("Step 3: Setting 'Login_Code' to NOT NULL and UNIQUE...")
        conn.execute(text('ALTER TABLE employees ALTER COLUMN "Login_Code" SET NOT NULL;'))
        conn.execute(text('ALTER TABLE employees ADD CONSTRAINT uq_employees_login_code UNIQUE ("Login_Code");'))
        
        print("Step 4: Creating index...")
        conn.execute(text('CREATE INDEX ix_employees_Login_Code ON employees ("Login_Code");'))
        conn.commit()

        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
