from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import models, schemas, crud, auth
from app.database import engine, get_db

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Login API", version="1.0.0")

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.security import OAuth2PasswordBearer

# ─── OAuth2 Scheme ────────────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="verify-otp")


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Login API is running"}


# ─── Register ─────────────────────────────────────────────────────────────────
@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_phone(db, user.phone)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered",
        )
    return crud.create_user(db, user)


# ─── Send OTP ─────────────────────────────────────────────────────────────────
@app.post("/send-otp", response_model=schemas.OTPResponse)
def send_otp(request: schemas.SendOTPRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_phone(db, request.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not registered. Please register first.",
        )
    otp = crud.generate_otp()
    crud.save_otp(db, request.phone, otp)
    print(f"[DEV] OTP for {request.phone}: {otp}")
    return schemas.OTPResponse(message="OTP sent successfully", otp=otp)


# ─── Verify OTP / Login ───────────────────────────────────────────────────────
@app.post("/verify-otp", response_model=schemas.Token)
def verify_otp(request: schemas.VerifyOTPRequest, db: Session = Depends(get_db)):
    valid = crud.verify_otp(db, request.phone, request.otp)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP",
        )
    access_token = auth.create_access_token(data={"sub": request.phone})
    return schemas.Token(access_token=access_token, token_type="bearer")


# ─── Get Current User ─────────────────────────────────────────────────────────
@app.get("/me", response_model=schemas.UserResponse)
def get_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    phone = auth.decode_access_token(token)
    if not phone:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user = crud.get_user_by_phone(db, phone)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
