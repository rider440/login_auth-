from app.database import engine
from sqlalchemy import text

def add_columns():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE otp_store ADD COLUMN attempts INTEGER DEFAULT 0"))
            conn.commit()
            print("Added column 'attempts' to 'otp_store'")
        except Exception as e:
            print(f"Error adding 'attempts': {e}")

        try:
            conn.execute(text("ALTER TABLE otp_store ADD COLUMN blocked_until TIMESTAMP WITH TIME ZONE"))
            conn.commit()
            print("Added column 'blocked_until' to 'otp_store'")
        except Exception as e:
            print(f"Error adding 'blocked_until': {e}")

if __name__ == "__main__":
    add_columns()
