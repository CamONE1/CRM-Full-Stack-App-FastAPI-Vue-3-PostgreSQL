"""
Seed script for Stage 0: 3 role users + 5-6 employees.

Idempotent — safe to run multiple times, skips records that already exist.
Run: python seed_data.py
"""
from datetime import date

from app.core.db import SessionLocal
from app.users.models import User, UserRole
from app.employees.models import Employee
from app.auth.security import hash_password


def get_or_create_user(db, email: str, password: str, role: UserRole) -> User:
	user = db.query(User).filter(User.email == email).first()
	if user:
		print("User already exists:", email)
		return user

	user = User(
		email=email,
		password_hash=hash_password(password),
		role=role,
		is_active=True,
	)
	db.add(user)
	db.commit()
	db.refresh(user)
	print("Created user:", email, f"({role.value})")
	return user


def get_or_create_employee(db, **kwargs) -> Employee:
	existing = db.query(Employee).filter(Employee.email == kwargs["email"]).first()
	if existing:
		print("Employee already exists:", kwargs["email"])
		return existing

	employee = Employee(**kwargs)
	db.add(employee)
	db.commit()
	db.refresh(employee)
	print("Created employee:", employee.full_name)
	return employee


def main():
	db = SessionLocal()

	# 3 role users
	admin = get_or_create_user(db, "admin@crm.com", "admin12345", UserRole.admin)
	hr = get_or_create_user(db, "hr@crm.com", "hr12345678", UserRole.hr)
	user = get_or_create_user(db, "user@crm.com", "user12345", UserRole.user)

	# Employees linked to a login (1:1 via user_id)
	get_or_create_employee(
		db,
		user_id=admin.id,
		full_name="Иван Соколов",
		email="i.sokolov@crm.com",
		phone="+7 900 111-22-33",
		department="IT",
		position="Системный администратор",
		hire_date=date(2022, 3, 1),
		is_active=True,
	)
	get_or_create_employee(
		db,
		user_id=hr.id,
		full_name="Мария Кузнецова",
		email="m.kuznetsova@crm.com",
		phone="+7 900 222-33-44",
		department="HR",
		position="HR-менеджер",
		hire_date=date(2022, 6, 15),
		is_active=True,
	)
	get_or_create_employee(
		db,
		user_id=user.id,
		full_name="Пётр Иванов",
		email="p.ivanov@crm.com",
		phone="+7 900 333-44-55",
		department="Development",
		position="Backend-разработчик",
		hire_date=date(2023, 1, 10),
		is_active=True,
	)

	# Employees without a login account
	get_or_create_employee(
		db,
		user_id=None,
		full_name="Анна Смирнова",
		email="a.smirnova@crm.com",
		phone="+7 900 444-55-66",
		department="Finance",
		position="Бухгалтер",
		hire_date=date(2021, 9, 1),
		is_active=True,
	)
	get_or_create_employee(
		db,
		user_id=None,
		full_name="Дмитрий Волков",
		email="d.volkov@crm.com",
		phone="+7 900 555-66-77",
		department="Sales",
		position="Менеджер по продажам",
		hire_date=date(2023, 4, 20),
		is_active=True,
	)
	get_or_create_employee(
		db,
		user_id=None,
		full_name="Елена Новикова",
		email="e.novikova@crm.com",
		phone="+7 900 666-77-88",
		department="Design",
		position="UI/UX-дизайнер",
		hire_date=date(2023, 8, 5),
		is_active=False,
	)

	db.close()
	print("Seeding done.")


if __name__ == "__main__":
	main()
