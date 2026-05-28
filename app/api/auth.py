from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import hashlib

from app.db.init_db import get_db
from app.models.user import User, Role
from app.auth.jwt import create_token

router = APIRouter(prefix="/auth", tags=["认证"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str
    user_id: int
    username: str


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        if db.query(User).filter(User.username == req.username).first():
            raise HTTPException(status_code=400, detail="用户名已存在")

        user_role = db.query(Role).filter(Role.name == "user").first()
        if not user_role:
            raise HTTPException(status_code=500, detail="系统角色未初始化")

        user = User(
            username=req.username,
            password_hash=hash_password(req.password),
            email=req.email,
        )
        user.roles.append(user_role)
        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_token(str(user.id), "user")
        return {"token": token, "user_id": user.id, "username": user.username}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    role_name = user.roles[0].name if user.roles else "user"
    token = create_token(str(user.id), role_name)
    return {"token": token, "user_id": user.id, "username": user.username}
