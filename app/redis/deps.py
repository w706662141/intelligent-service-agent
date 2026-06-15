import asyncio

from redis.asyncio import Redis
from app.redis.connection import redis_manager
from app.memory.redis_memory import RedisMemory


async def get_redis_client() -> Redis:
    """获取一个 Redis 客户端连接"""
    if redis_manager.pool is None:
        raise RuntimeError("Redis 连接池尚未初始化！请先调用 redis_manager.init_pool()")
    return Redis(connection_pool=redis_manager.pool)


async def get_redis_memory() -> RedisMemory:
    """直接获取封装好 client 的 RedisMemory 服务"""
    client = await get_redis_client()
    return RedisMemory(redis_client=client, max_messages=20)


async def main_test():
    print("1. 正在初始化全局连接池...")
    redis_manager.init_pool()  # 必须先初始化，否则 get_redis_client 会 raise
    print("2. 正在通过依赖函数获取 Redis 客户端...")
    client = await get_redis_client()

    print("3. 正在向 6399 端口发送 PING 验证网络...")
    if await client.ping():
        print("🟢 [Success] Redis 客户端获取并连接成功！")

    print("4. 正在测试 RedisMemory 记忆组件的流转...")
    # 顺便测试一下你的 Agent 记忆组件能不能正常拿到 client
    memory_service = await get_redis_memory()
    print("🟢 [Success] RedisMemory 服务初始化成功！")

    # 提示：在这里你可以顺便调用一下 memory_service 的方法
    # 比如：await memory_service.save_context(...) 来确保记忆组件也没 Bug
    if await client.ping():
        print("🟢 [Success] Redis 客户端获取并连接成功！")

if __name__ == '__main__':
    # 👇 异步的唯一正确启动姿势
    asyncio.run(main_test())