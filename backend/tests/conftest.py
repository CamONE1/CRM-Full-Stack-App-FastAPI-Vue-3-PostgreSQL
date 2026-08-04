import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal
from app.users.models import User, UserRole
from app.employees.models import Employee
from app.auth.security import hash_password


@pytest.fixture()
def client() -> TestClient:
	"""
	TestClient — это как Postman, только автоматический.
	Он вызывает твои эндпоинты прямо внутри Python.
	"""
	return TestClient(app)


@pytest.fixture()
def db():
	"""
	Даёт прямую сессию к базе, чтобы создавать тестовые данные.
	"""
	session = SessionLocal()
	try:
		yield session
	finally:
		session.close()


@pytest.fixture()
def admin_user(db) -> User:
	"""
	Создаём тестового админа напрямую в БД.
	Это делает тесты независимыми от seed_admin.py.
	"""
	email = "admin_test@crm.com"
	password = "admin12345"

	user = db.query(User).filter(User.email == email).first()
	if not user:
		user = User(
			email=email,
			password_hash=hash_password(password),
			role=UserRole.admin,
			is_active=True,
		)
		db.add(user)
		db.commit()
		db.refresh(user)

	# У news.author_id — FK на employees, поэтому у автора-админа
	# должен быть привязанный Employee (принцип "employees — source of truth").
	employee = db.query(Employee).filter(Employee.user_id == user.id).first()
	if not employee:
		employee = Employee(
			user_id=user.id,
			full_name="Test Admin",
			email="admin_test.employee@crm.com",
			is_active=True,
		)
		db.add(employee)
		db.commit()

	return user


@pytest.fixture()
def admin_tokens(client: TestClient, admin_user: User) -> dict:
	"""
	Получаем токены так же, как это сделает фронт:
	POST /auth/login → access_token + refresh_token.
	"""
	resp = client.post(
		"/auth/login",
		json={"email": admin_user.email, "password": "admin12345"},
	)
	assert resp.status_code == 200, resp.text
	return resp.json()


@pytest.fixture()
def plain_user(db) -> User:
	"""
	Пользователь с ролью user — для проверки, что RBAC реально запрещает доступ.
	"""
	email = "user_test@crm.com"
	password = "user12345"

	user = db.query(User).filter(User.email == email).first()
	if user:
		return user

	user = User(
		email=email,
		password_hash=hash_password(password),
		role=UserRole.user,
		is_active=True,
	)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user


@pytest.fixture()
def plain_user_tokens(client: TestClient, plain_user: User) -> dict:
	resp = client.post(
		"/auth/login",
		json={"email": plain_user.email, "password": "user12345"},
	)
	assert resp.status_code == 200, resp.text
	return resp.json()