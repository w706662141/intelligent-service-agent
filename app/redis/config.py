import os
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    # 默认连接本地，生产环境可以通过环境变量覆盖
    REDIS_HOST: str = os.getenv('REDIS_HOST', "127.0.0.1")
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', '6399'))
    REDIS_PASSWORD: str | None = os.getenv("REDIS_PASSWORD", None)
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))

    @property
    def url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


redis_settings = RedisSettings()

