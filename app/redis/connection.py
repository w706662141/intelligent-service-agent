from redis.asyncio import ConnectionPool
from app.redis.config import redis_settings


class RedisManager:
    def __init__(self):
        self.pool: ConnectionPool | None = None

    def init_pool(self):
        """初始化全局连接池"""
        # decode_responses=True 解决你之前遇到的各种字节码/黄色警告问题
        self.pool = ConnectionPool.from_url(
            redis_settings.url,
            decode_responses=True
        )

    async def close_pool(self):
        """关闭全局连接池"""
        if self.pool:
            self.pool.disconnect()


redis_manager = RedisManager()

