from dataclasses import dataclass

from passlib.context import CryptContext

from app.auth.tokens import create_access_token


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class User:
    user_id: str
    hashed_password: str
    role: str


# Pilot-only static user store; replace with DB/SSO in v2.
# Passwords are bcrypt-hashed at module load time.
USER_STORE = {
    "employee": User(
        user_id="employee",
        hashed_password=pwd_context.hash("employee123"),
        role="employee",
    ),
    "admin": User(
        user_id="admin",
        hashed_password=pwd_context.hash("admin123"),
        role="admin",
    ),
}


def authenticate_user(username: str, password: str):
    user = USER_STORE.get(username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    token = create_access_token(user_id=user.user_id, role=user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "role": user.role,
    }
