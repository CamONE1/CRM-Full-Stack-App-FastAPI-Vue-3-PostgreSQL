from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.employees import schemas
from app.employees.models import Employee


def get_employees(
	db: Session,
	search: str | None = None,
	position: str | None = None,
	is_active: bool | None = None,
	offset: int = 0,
	limit: int = 50,
) -> tuple[list[Employee], int]:
	query = db.query(Employee)

	if search:
		like = f"%{search}%"
		query = query.filter(or_(Employee.full_name.ilike(like), Employee.email.ilike(like)))
	if position:
		query = query.filter(Employee.position == position)
	if is_active is not None:
		query = query.filter(Employee.is_active == is_active)

	total = query.count()
	items = query.order_by(Employee.full_name).offset(offset).limit(limit).all()
	return items, total


def get_employee(db: Session, employee_id: int) -> Employee | None:
	return db.get(Employee, employee_id)


def get_employee_by_user_id(db: Session, user_id: int) -> Employee | None:
	return db.query(Employee).filter(Employee.user_id == user_id).first()


def get_distinct_positions(db: Session) -> list[str]:
	rows = (
		db.query(Employee.position)
		.filter(Employee.position.isnot(None))
		.distinct()
		.order_by(Employee.position)
		.all()
	)
	return [row[0] for row in rows]


def update_employee_self(db: Session, employee: Employee, data: schemas.EmployeeSelfUpdate) -> Employee:
	updates = data.model_dump(exclude_unset=True)
	for field, value in updates.items():
		setattr(employee, field, value)
	db.commit()
	db.refresh(employee)
	return employee
