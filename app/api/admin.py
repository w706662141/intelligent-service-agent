from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.init_db import get_db
from app.models.user import User, Role, Permission
from app.auth.permissions import get_current_user, require_permission

router = APIRouter(prefix="/admin", tags=["管理后台"])


# ---- Schemas ----

class RoleCreate(BaseModel):
    name: str
    description: str | None = None


class PermissionCreate(BaseModel):
    name: str
    description: str | None = None


class AssignRole(BaseModel):
    role_name: str


class AssignPermission(BaseModel):
    permission_name: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str | None
    is_active: bool
    roles: list[str]

    class Config:
        from_attributes = True


class RoleOut(BaseModel):
    id: int
    name: str
    description: str | None
    permissions: list[str]

    class Config:
        from_attributes = True


# ---- 用户管理 ----

@router.get("/users", response_model=list[UserOut])
def list_users(
    current_user: User = require_permission("user:manage"),
    db: Session = Depends(get_db),
):
    """获取用户列表"""
    users = db.query(User).all()
    return [
        UserOut(
            id=u.id,
            username=u.username,
            email=u.email,
            is_active=u.is_active,
            roles=[r.name for r in u.roles],
        )
        for u in users
    ]


@router.put("/users/{user_id}/toggle")
def toggle_user(
    user_id: int,
    current_user: User = require_permission("user:manage"),
    db: Session = Depends(get_db),
):
    """启用/禁用用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = not user.is_active
    db.commit()
    return {"user_id": user_id, "is_active": user.is_active}


@router.post("/users/{user_id}/roles")
def assign_role_to_user(
    user_id: int,
    req: AssignRole,
    current_user: User = require_permission("user:manage"),
    db: Session = Depends(get_db),
):
    """为用户分配角色"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    role = db.query(Role).filter(Role.name == req.role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
    return {"user_id": user_id, "role": req.role_name}


@router.delete("/users/{user_id}/roles/{role_name}")
def remove_role_from_user(
    user_id: int,
    role_name: str,
    current_user: User = require_permission("user:manage"),
    db: Session = Depends(get_db),
):
    """移除用户角色"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role in user.roles:
        user.roles.remove(role)
        db.commit()
    return {"user_id": user_id, "removed_role": role_name}


# ---- 角色管理 ----

@router.get("/roles", response_model=list[RoleOut])
def list_roles(
    current_user: User = require_permission("user:manage"),
    db: Session = Depends(get_db),
):
    """获取角色列表"""
    roles = db.query(Role).all()
    return [
        RoleOut(
            id=r.id,
            name=r.name,
            description=r.description,
            permissions=[p.name for p in r.permissions],
        )
        for r in roles
    ]


@router.post("/roles", response_model=RoleOut)
def create_role(
    req: RoleCreate,
    current_user: User = require_permission("user:manage"),
    db: Session = Depends(get_db),
):
    """创建角色"""
    if db.query(Role).filter(Role.name == req.name).first():
        raise HTTPException(status_code=400, detail="角色名已存在")
    role = Role(name=req.name, description=req.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return RoleOut(id=role.id, name=role.name, description=role.description, permissions=[])


@router.post("/roles/{role_id}/permissions")
def assign_permission_to_role(
    role_id: int,
    req: AssignPermission,
    current_user: User = require_permission("user:manage"),
    db: Session = Depends(get_db),
):
    """为角色分配权限"""
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        perm = db.query(Permission).filter(Permission.name == req.permission_name).first()
        if not perm:
            raise HTTPException(status_code=404, detail="权限不存在")
        if perm not in role.permissions:
            role.permissions.append(perm)
            db.commit()
        return {"role_id": role_id, "permission": req.permission_name}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ---- 权限管理 ----

@router.get("/permissions")
def list_permissions(
    current_user: User = require_permission("user:manage"),
    db: Session = Depends(get_db),
):
    """获取权限列表"""
    perms = db.query(Permission).all()
    return [{"id": p.id, "name": p.name, "description": p.description} for p in perms]


@router.post("/permissions")
def create_permission(
    req: PermissionCreate,
    current_user: User = require_permission("user:manage"),
    db: Session = Depends(get_db),
):
    """创建权限"""
    if db.query(Permission).filter(Permission.name == req.name).first():
        raise HTTPException(status_code=400, detail="权限名已存在")
    perm = Permission(name=req.name, description=req.description)
    db.add(perm)
    db.commit()
    return {"id": perm.id, "name": perm.name, "description": perm.description}
