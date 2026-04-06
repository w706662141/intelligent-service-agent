from sqlalchemy import text

from app.db.database import get_connection, get_mysql_connection


def init_db():
    with get_mysql_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO department (name, location) VALUES
        ('HR', '北京'),
        ('IT', '上海');
        """)
        cursor.execute("""  
        INSERT INTO employee (employee_id, name, department_id, role, hire_date) VALUES
        ('E001', '张三', 1, '经理', '2020-01-01'),
        ('E002', '李四', 2, '工程师', '2021-06-01');
                """)
        cursor.execute("""  
        INSERT INTO orders (employee_id, amount, status, created_at) VALUES
        ('E001', 5000.00, 'completed', NOW()),
        ('E001', 2000.00, 'pending', NOW()),
        ('E002', 8000.00, 'completed', NOW());
                """)

        conn.commit()
        cursor.close()

def test_db():

    data_list=[
        {'new_order_id':10001,"old_order_id":'1'},
        {'new_order_id':10002,"old_order_id":'2'},
        {'new_order_id':10003,"old_order_id":'3'},
    ]

    alter_sql="""
    update  orders set order_id= :new_order_id where order_id= :old_order_id
    """

    with get_mysql_connection() as conn:

        conn.execute(text(alter_sql),data_list)

        conn.commit()

if __name__ == '__main__':
    test_db()
