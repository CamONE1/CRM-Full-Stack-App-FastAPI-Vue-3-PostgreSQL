from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.users.models import User
from app.auth.schemas import LoginRequest, TokenPair, MeResponse
from app.auth.security import (
	verify_password,
	create_access_token,
	create_refresh_token,
	JWT_SECRET,
	JWT_ALG,
)

router = APIRouter(
	prefix="/auth",
	tags=["Auth"]
)
bearer = HTTPBearer(auto_error=False)


def get_user_by_email(db: Session, email: str) -> User | None:
	return db.query(User).filter(User.email == email).first()


def decode_token(token: str) -> dict:
	try:
		return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
	except JWTError:
		raise HTTPException(status_code=401, detail="Invalid token")


@router.post(
	"/login",
	response_model=TokenPair
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
	user = get_user_by_email(db, data.email)
	if not user or not verify_password(data.password, user.password_hash):
		raise HTTPException(status_code=401, detail="Invalid email or password")
	if not user.is_active:
		raise HTTPException(status_code=403, detail="User is inactive")

	return TokenPair(
		access_token=create_access_token(user.id, user.role.value),
		refresh_token=create_refresh_token(user.id),
	)


@router.post(
	"/refresh",
	response_model=TokenPair
)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
	payload = decode_token(refresh_token)
	if payload.get("type") != "refresh":
		raise HTTPException(status_code=401, detail="Invalid refresh token type")

	user_id = int(payload["sub"])
	user = db.get(User, user_id)
	if not user or not user.is_active:
		raise HTTPException(status_code=401, detail="User not found or inactive")

	return TokenPair(
		access_token=create_access_token(user.id, user.role.value),
		refresh_token=create_refresh_token(user.id),
	)


@router.get(
	"/me",
	response_model=MeResponse
)
def me(creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
	if creds is None:
		raise HTTPException(status_code=401, detail="Missing Authorization header")

	payload = decode_token(creds.credentials)
	if payload.get("type") != "access":
		raise HTTPException(status_code=401, detail="Invalid access token type")

	user_id = int(payload["sub"])
	user = db.get(User, user_id)
	if not user:
		raise HTTPException(status_code=401, detail="User not found")

	return MeResponse(id=user.id, email=user.email, role=user.role.value)