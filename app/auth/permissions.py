from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.auth.jwt import verify_token
from app.db.init_db import get_db
from app.models.user import User, Permission, user_roles, role_permissions


def get_current_user(
        token_payload: dict = Depends(verify_token),
        db: Session = Depends(get_db)
) -> User:
    """从 token 获取当前用户"""
    user_id = token_payload.get('sub')
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user


# def get_user_permissions(db: Session, user_id: int) -> list:
#     """获取用户的所有权限名称"""
#     result = db.execute(
#         select(Permission.name)
#             .join(role_permissions, role_permissions.c.permission_id == Permission.id)
#             .join(user_roles, user_roles.c.role_id == role_permissions.c.role_id)
#             .where(user_roles.c.user_id == user_id)
#     ).fetchall()
#     return [row[0] for row in result]
def get_user_permissions(db: Session, user_id: int) -> list:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    return [perm.name for role in user.roles for perm in role.permissions]


def require_permission(permission: str):
    """权限检查依赖项"""

    def dependency(
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
    ):
        perms = get_user_permissions(db, current_user.id)
        if permission not in perms:
            raise HTTPException(status_code=403, detail=f"权限不足，需要: {permission}")
        return current_user

    return Depends(dependency)
