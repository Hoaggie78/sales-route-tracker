from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory session store (use Redis/Database in production)
token_sessions = {}


def create_session(microsoft_token: str, refresh_token: Optional[str] = None) -> str:
    import secrets
    session_id = secrets.token_urlsafe(32)
    token_sessions[session_id] = {
        "microsoft_token": microsoft_token,
        "refresh_token": refresh_token
    }
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    return token_sessions.get(session_id)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    TEST_KEY = "testsecret"
    import hashlib
    key_hash = hashlib.md5(TEST_KEY.encode()).hexdigest()
    print(f"DEBUG: Encoding with Key Hash: {key_hash}")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, TEST_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        TEST_KEY = "testsecret"
        import hashlib
        key_hash = hashlib.md5(TEST_KEY.encode()).hexdigest()
        print(f"DEBUG: Decoding with Key Hash: {key_hash}")
        print(f"DEBUG: Token='{token}'")
        payload = jwt.decode(token, TEST_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        print(f"JWT DECODE ERROR: {str(e)}")
        return None
