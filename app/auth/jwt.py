import os
import time

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM = "HS256"
EXPIRE_SECONDS = 7200

security = HTTPBearer()


def create_token(user_id: str, role: str = "user") -> str:
    """签发 JWT（测试用，正式环境由认证服务签发）"""
    payload = {
        "sub": user_id,
        "role": role,
        "exp": int(time.time()) + EXPIRE_SECONDS,
        "iat": int(time.time()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """FastAPI 依赖项：从 Authorization: Bearer <token> 解析用户信息"""
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token 无效")
