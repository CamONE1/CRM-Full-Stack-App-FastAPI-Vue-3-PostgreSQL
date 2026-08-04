from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.users.models import UserRole


class UserOut(BaseModel):
	id: int
	email: str
	role: UserRole
	is_active: bool
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
	role: UserRole | None = None
	is_active: bool | None = None
