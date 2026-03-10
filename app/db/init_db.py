from app.db.database import get_connection


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees(
    employee_id TEXT PRIMARY KEY,
    name TEXT,
    department TEXT,
    role TEXT
    )
    """)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print('数据库初始化完成')
