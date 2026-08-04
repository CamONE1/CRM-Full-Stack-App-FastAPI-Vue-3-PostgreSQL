# GET /users без токена → 401
def test_list_users_without_token_is_401(client):
	resp = client.get("/users")
	assert resp.status_code == 401


# GET /users с ролью user (не admin) → 403
def test_list_users_as_non_admin_is_403(client, plain_user_tokens: dict):
	access = plain_user_tokens["access_token"]
	resp = client.get("/users", headers={"Authorization": f"Bearer {access}"})
	assert resp.status_code == 403


# GET /users с ролью admin → 200 и содержит тестового админа
def test_list_users_as_admin_is_200(client, admin_tokens: dict, admin_user):
	access = admin_tokens["access_token"]
	resp = client.get("/users", headers={"Authorization": f"Bearer {access}"})
	assert resp.status_code == 200, resp.text

	emails = [u["email"] for u in resp.json()]
	assert admin_user.email in emails


# PATCH /users/{id} с ролью user (не admin) → 403
def test_patch_user_as_non_admin_is_403(client, plain_user_tokens: dict, plain_user):
	access = plain_user_tokens["access_token"]
	resp = client.patch(
		f"/users/{plain_user.id}",
		json={"is_active": False},
		headers={"Authorization": f"Bearer {access}"},
	)
	assert resp.status_code == 403


# PATCH /users/{id} с ролью admin меняет role и is_active, затем возвращает исходное состояние
def test_patch_user_as_admin_updates_fields(client, admin_tokens: dict, plain_user):
	access = admin_tokens["access_token"]

	resp = client.patch(
		f"/users/{plain_user.id}",
		json={"role": "hr", "is_active": False},
		headers={"Authorization": f"Bearer {access}"},
	)
	assert resp.status_code == 200, resp.text
	data = resp.json()
	assert data["role"] == "hr"
	assert data["is_active"] is False

	# возвращаем как было, чтобы не влиять на другие тесты, использующие plain_user
	resp = client.patch(
		f"/users/{plain_user.id}",
		json={"role": "user", "is_active": True},
		headers={"Authorization": f"Bearer {access}"},
	)
	assert resp.status_code == 200, resp.text


# PATCH /users/{id} для несуществующего id → 404
def test_patch_nonexistent_user_is_404(client, admin_tokens: dict):
	access = admin_tokens["access_token"]
	resp = client.patch(
		"/users/999999",
		json={"is_active": False},
		headers={"Authorization": f"Bearer {access}"},
	)
	assert resp.status_code == 404
