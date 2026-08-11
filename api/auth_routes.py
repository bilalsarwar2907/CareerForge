from fastapi import APIRouter, HTTPException
from api.models import RegisterRequest, LoginRequest, TokenResponse
from api.auth import create_user, get_user, verify_password, create_access_token, init_users_table

router = APIRouter(prefix="/auth")

init_users_table()


@router.post("/register", response_model=dict)
def register(req: RegisterRequest):
    success = create_user(req.username, req.password)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"registered": True}


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = get_user(req.username)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(req.username)
    return {"access_token": token}