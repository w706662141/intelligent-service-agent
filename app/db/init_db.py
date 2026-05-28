from sqlalchemy.orm import sessionmaker
from app.db.database_pools import POOL
from app.db.base import Base

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=POOL)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    # Base.metadata.create_all(bind=POOL)
    seed_data()


def seed_data():
    from app.models.user import Role, Permission, role_permissions, User
    import hashlib

    db = SessionLocal()

    try:
        # 创建权限（如果不存在）
        permissions_data = [
            ('chat:send', '发送消息'),
            ('chat:stream', '流式对话'),
            ('history:read', '查看历史对话'),
            ('history:delete', '删除历史对话'),
            ('session:manage', '管理会话'),
            ('user:manage', '管理用户'),
        ]
        for name, desc in permissions_data:
            if not db.query(Permission).filter(Permission.name == name).first():
                db.add(Permission(name=name, description=desc))
        db.flush()

        # 创建角色（如果不存在）
        roles_data = [
            ('admin', '管理员'),
            ('user', '普通用户'),
            ('viewer', '只读用户'),
        ]
        for name, desc in roles_data:
            if not db.query(Role).filter(Role.name == name).first():
                db.add(Role(name=name, description=desc))
        db.flush()

        # 角色-权限关联（确保已设置）
        admin_role = db.query(Role).filter(Role.name == 'admin').first()
        user_role = db.query(Role).filter(Role.name == 'user').first()
        viewer_role = db.query(Role).filter(Role.name == 'viewer').first()

        all_perms = db.query(Permission).all()
        perm_map = {p.name: p for p in all_perms}

        # admin: 所有权限
        if not admin_role.permissions:
            admin_role.permissions = list(all_perms)

        # user: 聊天+历史+会话管理
        if not user_role.permissions:
            user_role.permissions = [perm_map[p] for p in
                                     ['chat:send', 'chat:stream', 'history:read', 'history:delete', 'session:manage']]

        # viewer: 只读
        if not viewer_role.permissions:
            viewer_role.permissions = [perm_map['history:read']]

        # 创建默认管理员账号（如果不存在）
        admin_user = db.query(User).filter(User.username == 'admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                password_hash=hashlib.sha256('admin123'.encode()).hexdigest(),
                email='admin@system.local',
            )
            admin_user.roles.append(admin_role)
            db.add(admin_user)
        elif admin_role not in admin_user.roles:
            admin_user.roles.append(admin_role)

        db.commit()
    finally:
        db.close()


if __name__ == '__main__':
    init_database()

