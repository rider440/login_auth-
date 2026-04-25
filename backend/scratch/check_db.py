from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def check_all_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    for table in tables:
        print(f"\nColumns in '{table}' table:")
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"- {column['name']} ({column['type']})")

if __name__ == "__main__":
    check_all_tables()
