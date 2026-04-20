from fastapi import APIRouter, HTTPException, status

from app.api.schemas.auth import LoginRequest, LoginResponse
from app.auth.service import authenticate_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    token_payload = authenticate_user(payload.username, payload.password)
    if not token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/password",
        )
    return token_payload
