from app.db.database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
INSERT OR REPLACE INTO employees VALUES
    ('E001','张三','HR','经理'),
    ('E002','李四','IT','工程师'),
    ('E003','王五','IT','架构师')
""")

conn.commit()
conn.close()
print('数据添加完成')