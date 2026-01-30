import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal
from app.users.models import User, UserRole
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
	if user:
		return user

	user = User(
		email=email,
		password_hash=hash_password(password),
		role=UserRole.admin,
		is_active=True,
	)
	db.add(user)
	db.commit()
	db.refresh(user)
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