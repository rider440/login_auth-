from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

from app.database import engine, Base
from app.models import Employee_model, Project_model, Task_model, Teams_model, Assign_task_model

def sync():
    # Create new tables first
    Base.metadata.create_all(bind=engine)
    print("Created/Verified all tables.")
    
    with engine.connect() as conn:
        # Helper to safely add column
        def add_column(table, col_def):
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_def}"))
                conn.commit()
                print(f"Added column to {table}")
            except Exception as e:
                conn.rollback()
                print(f"Column in {table} might exist: {str(e).splitlines()[0]}")

        add_column("employees", "\"Role\" VARCHAR DEFAULT 'employee'")
        add_column("tasks", "project_id INTEGER REFERENCES projects(\"ProjectId\") ON DELETE CASCADE")
        add_column("tasks", "team_id INTEGER REFERENCES teams(\"TeamId\") ON DELETE SET NULL")

if __name__ == "__main__":
    sync()
