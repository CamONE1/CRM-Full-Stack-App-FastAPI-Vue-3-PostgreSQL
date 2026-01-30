from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Потом вынесем в .env, сейчас фиксируем для старта
JWT_SECRET = "dev_secret_change_me"
JWT_ALG = "HS256"

ACCESS_TTL_MIN = 15
REFRESH_TTL_DAYS = 14


def hash_password(password: str) -> str:
	return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
	return pwd_context.verify(password, password_hash)


def create_access_token(user_id: int, role: str) -> str:
	now = datetime.now(timezone.utc)
	payload = {
		"sub": str(user_id),
		"role": role,
		"type": "access",
		"iat": int(now.timestamp()),
		"exp": int((now + timedelta(minutes=ACCESS_TTL_MIN)).timestamp()),
	}
	return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_refresh_token(user_id: int) -> str:
	now = datetime.now(timezone.utc)
	payload = {
		"sub": str(user_id),
		"type": "refresh",
		"iat": int(now.timestamp()),
		"exp": int((now + timedelta(days=REFRESH_TTL_DAYS)).timestamp()),
	}
	return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)