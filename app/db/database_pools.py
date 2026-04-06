from sqlalchemy import create_engine


POOL=create_engine(
    "mysql+pymysql://root:root@localhost:3306/agent_service",
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False
)

