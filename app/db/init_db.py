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
    from app.models.user import Role, Permission, role_permissions

    db = SessionLocal()

    try:
        if db.query(Role).first():
            return

        # 创建权限
        permissions_data = [
            ('chat:send', '发送消息'),
            ('chat:stream', '流式对话'),
            ('history:read', '查看历史对话'),
            ('history:delete', '删除历史对话'),
            ('session:manage', '管理会话'),
            ('user:manage', '管理用户'),
        ]
        perm_ids = {}
        for name, desc in permissions_data:
            p = Permission(name=name, description=desc)
            db.add(p)
            db.flush()
            perm_ids[name] = p.id

        # 创建角色
        roles_data = [
            ('admin', '管理员'),
            ('user', '普通用户'),
            ('viewer', '只读用户'),
        ]
        role_ids = {}
        for name, desc in roles_data:
            r = Role(name=name, description=desc)
            db.add(r)
            db.flush()
            role_ids[name] = r.id

        # 角色-权限关联
        admin_perms = list(perm_ids.values())
        user_perms = [perm_ids[p] for p in
                      ['chat:send', 'chat:stream', 'history:read', 'history:delete', 'session:manage']]
        viewer_perms = [perm_ids['history:read']]

        for perm_id in admin_perms:
            db.execute(role_permissions.insert().values(role_id=role_ids['admin'], permission_id=perm_id))
        for perm_id in user_perms:
            db.execute(role_permissions.insert().values(role_id=role_ids['user'], permission_id=perm_id))
        for perm_id in viewer_perms:
            db.execute(role_permissions.insert().values(role_id=role_ids['viewer'], permission_id=perm_id))
        db.commit()
    finally:
        db.close()


if __name__ == '__main__':
    init_database()

