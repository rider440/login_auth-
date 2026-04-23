# Backend Documentation: Login & Registration API

## 📂 Folder Structure

```text
Login/v 
├── backend/
│   ├── app/
│   │   ├── auth.py         # JWT & Security logic
│   │   ├── crud.py         # Database operations (Create, Read, Update, Delete)
│   │   ├── database.py     # Connection setup & session management
│   │   ├── main.py         # FastAPI routes & entry point
│   │   ├── models.py       # SQLAlchemy Database models (Tables)
│   │   └── schemas.py      # Pydantic data validation schemas
│   ├── .env                # Environment variables (DB URL, Secrets)
│   └── BACKEND_GUIDE.md    # This documentation
└── frontend/               # Next.js Application
    ├── app/                # Pages & Routing
    ├── components/         # Reusable UI components
    └── services/           # API communication layer
```

## 📄 File Responsibilities

### 1. `main.py` (The Entry Point)
- **Purpose**: Initializes the FastAPI application and defines the API endpoints (Routes).
- **Key Functions**:
    - Configures CORS (Cross-Origin Resource Sharing) to allow the frontend to communicate with the backend.
    - Defines routes like `/register`, `/send-otp`, `/verify-otp`, and `/me`.
    - Coordinates the flow between request validation (Schemas), database logic (CRUD), and authentication (Auth).

### 2. `models.py` (The Database Structure)
- **Purpose**: Defines how the data is stored in the database using SQLAlchemy.
- **Why use Models?**: 
    - Models represent the physical tables in your PostgreSQL database.
    - They allow us to interact with the database using Python objects instead of writing raw SQL queries.
- **Tables**:
    - `User`: Stores user profile details (Name, Phone, Address, City).
    - `OTPStore`: Stores temporary verification codes sent to users.

### 3. `schemas.py` (Data Validation)
- **Purpose**: Defines Pydantic models for request and response data.
- **Why use Schemas?**:
    - They ensure that the data coming from the frontend is valid (e.g., correct data types).
    - They control what data is sent back to the frontend (e.g., hiding sensitive information like internal IDs).

### 4. `crud.py` (Database Logic)
- **Purpose**: Contains all functions that directly interact with the database (Create, Read, Update, Delete).
- **Key Functions**:
    - `get_user_by_phone`: Finds a user in the database.
    - `create_user`: Saves a new user.
    - `generate_otp` & `save_otp`: Handles the verification code lifecycle.

### 5. `database.py` (Connection Management)
- **Purpose**: Sets up the connection to PostgreSQL using the `DATABASE_URL` from the `.env` file.
- **Key Components**:
    - `engine`: The engine that connects Python to PostgreSQL.
    - `SessionLocal`: A factory for creating database sessions.
    - `get_db()`: A dependency that provides a fresh database session for each API request and closes it afterward.

### 6. `auth.py` (Security)
- **Purpose**: Handles security-related tasks like generating and verifying JWT (JSON Web Tokens).
- **Key Functions**:
    - `create_access_token`: Generates a secure token after a user logs in.
    - `decode_access_token`: Validates the token when a user tries to access protected data.

---

## 🔄 How the Code Works (Data Flow)

### Example: User Login Flow
1. **Request**: The user enters their phone number on the frontend.
2. **Main**: `/send-otp` route is triggered in `main.py`.
3. **CRUD**: `main.py` calls `crud.generate_otp()` and saves it to the database.
4. **Response**: The OTP is logged to the console (in dev mode) and a success message is sent to the frontend.
5. **Verification**: The user enters the OTP. Frontend calls `/verify-otp`.
6. **Main**: `main.py` calls `crud.verify_otp()`.
7. **Auth**: If valid, `auth.create_access_token()` generates a JWT.
8. **Success**: The frontend receives the token and redirects to the Dashboard.

## 🛠 Setup & Connection
The backend uses a **.env** file to store sensitive configurations:
- `DATABASE_URL`: Connection string for PostgreSQL.
- `SECRET_KEY`: Used to sign security tokens.

To run the backend:
```bash
uvicorn app.main:app --reload
```
