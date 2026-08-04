from app.employees.models import Employee


# Проверяем, что /auth/login действительно выдаёт пару токенов
def test_login_returns_tokens(admin_tokens: dict):
	assert "access_token" in admin_tokens
	assert "refresh_token" in admin_tokens
	assert admin_tokens.get("token_type") == "bearer"


# POST /news без Authorization должен быть 401
def test_news_create_without_token_is_401(client):
	resp = client.post(
		"/news",
		json={"title": "t", "body": "b"},
	)
	assert resp.status_code == 401
	assert "Missing Authorization header" in resp.text


# Refresh токен нельзя использовать как access токен → 401
def test_news_create_with_refresh_token_is_401(client, admin_tokens: dict):
	refresh = admin_tokens["refresh_token"]
	resp = client.post(
		"/news",
		json={"title": "t", "body": "b"},
		headers={"Authorization": f"Bearer {refresh}"},
	)
	assert resp.status_code == 401
	assert "Invalid access token type" in resp.text


# Access токен admin должен позволить создать новость → 201
def test_news_create_with_access_token_is_201(client, admin_tokens: dict, admin_user, db):
	access = admin_tokens["access_token"]
	resp = client.post(
		"/news",
		json={"title": "hello", "body": "world"},
		headers={"Authorization": f"Bearer {access}"},
	)

	# У меня в роутере: status_code=status.HTTP_201_CREATED
	assert resp.status_code == 201, resp.text

	data = resp.json()
	assert data["title"] == "hello"
	assert data["body"] == "world"
	assert "id" in data

	# author_id должен указывать на Employee, привязанного к текущему пользователю
	author_employee = db.query(Employee).filter(Employee.user_id == admin_user.id).first()
	assert data["author_id"] == author_employee.id


# GET /news публичный (без токена) и использует offset/limit
def test_news_list_is_public_and_supports_pagination(client):
	resp = client.get("/news?offset=0&limit=10")
	assert resp.status_code == 200, resp.text
	assert isinstance(resp.json(), list)