from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.utils.config import settings
from typing import Optional


def create_access_token(data:dict)->str:
    to_encode=data.copy()
    expire=datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, settings.jwt_secret_key,algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
    
# Why JWT over server-side sessions? JWTs are stateless — the server doesn't need to store session data anywhere (no session table, no Redis lookup) because the token itself carries the proof of identity, cryptographically signed. This scales better horizontally: any server instance behind a load balancer can verify a token without shared session storage. The trade-off, and you should say this unprompted in an interview because it shows depth: you can't easily revoke a JWT before it expires. If a token is stolen, it's valid until exp hits, unless you build a token blacklist (defeats some of the statelessness benefit) or keep expiry short and use refresh tokens.