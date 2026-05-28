from typing import List

from sqlalchemy import Column, Table, Integer, String, Boolean, DateTime, select
from datetime import datetime, timezone
from app.db.base import Base
from sqlalchemy.orm import relationship, mapped_column, Mapped

user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, nullable=False, index=True, primary_key=True),
    Column('role_id', Integer, nullable=False, index=True, primary_key=True)
)

role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', Integer, nullable=False, index=True, primary_key=True),
    Column('permission_id', Integer, nullable=False, index=True, primary_key=True)
)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    email: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    roles: Mapped[List["Role"]] = relationship(
        secondary='user_roles',
        primaryjoin='User.id==user_roles.c.user_id',
        secondaryjoin='user_roles.c.role_id==Role.id',
        back_populates='users')

    def has_permission(self, perm_name: str) -> bool:
        """应用层关联检查，不依赖数据库外键"""
        return any(
            perm.name == perm_name
            for role in self.roles
            for perm in role.permissions
        )


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(String(200))

    users: Mapped[List["User"]] = relationship(secondary='user_roles',
                                               primaryjoin='Role.id==user_roles.c.role_id',
                                               secondaryjoin='user_roles.c.user_id==User.id',
                                               back_populates='roles')

    permissions: Mapped[List["Permission"]] = relationship(secondary='role_permissions',
                                                           primaryjoin='Role.id==role_permissions.c.role_id',
                                                           secondaryjoin='role_permissions.c.permission_id==Permission.id',
                                                           back_populates='roles')


class Permission(Base):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(200))

    roles: Mapped[List["Role"]] = relationship(secondary='role_permissions',
                                               primaryjoin='role_permissions.c.permission_id==Permission.id',
                                               secondaryjoin='role_permissions.c.role_id==Role.id',
                                               back_populates='permissions')
