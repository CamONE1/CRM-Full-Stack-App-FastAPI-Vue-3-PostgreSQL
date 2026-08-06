from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class EmployeeOut(BaseModel):
	id: int
	user_id: int | None
	full_name: str
	email: str
	phone: str | None
	telegram: str | None
	department: str | None
	position: str | None
	hire_date: date | None
	is_active: bool
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)


class EmployeeListOut(BaseModel):
	items: list[EmployeeOut]
	total: int


class EmployeeSelfUpdate(BaseModel):
	phone: str | None = None
	telegram: str | None = None
