from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.auth.security import JWT_SECRET, JWT_ALG

bearer = HTTPBearer(auto_error=False)


def get_current_user_payload(
	creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict:
	# 401: нет заголовка Authorization
	if creds is None:
		raise HTTPException(status_code=401, detail="Missing Authorization header")

	token = creds.credentials
	try:
		payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
	except JWTError:
		raise HTTPException(status_code=401, detail="Invalid token")

	# 401: подали refresh вместо access
	if payload.get("type") != "access":
		raise HTTPException(status_code=401, detail="Invalid access token type")

	return payload


def require_roles(*allowed_roles: str):
	def checker(payload: dict = Depends(get_current_user_payload)) -> dict:
		role = payload.get("role")
		# 403: токен валидный, но роль не подходит
		if role not in allowed_roles:
			raise HTTPException(status_code=403, detail="Forbidden")
		return payload
	
	return checker