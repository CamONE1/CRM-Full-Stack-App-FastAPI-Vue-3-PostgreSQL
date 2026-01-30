from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
	email: EmailStr
	password: str


class TokenPair(BaseModel):
	access_token: str
	refresh_token: str
	token_type: str = "bearer"


class MeResponse(BaseModel):
	id: int
	email: EmailStr
	role: str