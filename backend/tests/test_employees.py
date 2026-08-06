from app.employees.models import Employee


# GET /employees без токена → 401
def test_list_employees_without_token_is_401(client):
	resp = client.get("/employees")
	assert resp.status_code == 401


# GET /employees с ролью user (не hr/admin) → 403
def test_list_employees_as_plain_user_is_403(client, plain_user_tokens: dict):
	access = plain_user_tokens["access_token"]
	resp = client.get("/employees", headers={"Authorization": f"Bearer {access}"})
	assert resp.status_code == 403


# GET /employees с ролью admin → 200, есть employee админа, есть total
def test_list_employees_as_admin_is_200(client, admin_tokens: dict, admin_user, db):
	access = admin_tokens["access_token"]
	resp = client.get("/employees", headers={"Authorization": f"Bearer {access}"})
	assert resp.status_code == 200, resp.text

	data = resp.json()
	assert "items" in data and "total" in data
	emails = [e["email"] for e in data["items"]]
	admin_employee = db.query(Employee).filter(Employee.user_id == admin_user.id).first()
	assert admin_employee.email in emails


# GET /employees?search= фильтрует по имени/email
def test_list_employees_search_filters_by_name(client, admin_tokens: dict, db):
	access = admin_tokens["access_token"]
	employee = db.query(Employee).filter(Employee.email == "unique_search_target@crm.com").first()
	if not employee:
		employee = Employee(full_name="Zzz Searchable Target", email="unique_search_target@crm.com", is_active=True)
		db.add(employee)
		db.commit()

	resp = client.get(
		"/employees",
		params={"search": "Searchable Target"},
		headers={"Authorization": f"Bearer {access}"},
	)
	assert resp.status_code == 200, resp.text
	data = resp.json()
	assert data["total"] == 1
	assert data["items"][0]["email"] == "unique_search_target@crm.com"


# GET /employees?is_active=false фильтрует по статусу
def test_list_employees_filters_by_status(client, admin_tokens: dict, db):
	access = admin_tokens["access_token"]
	employee = db.query(Employee).filter(Employee.email == "inactive_target@crm.com").first()
	if not employee:
		employee = Employee(full_name="Inactive Target", email="inactive_target@crm.com", is_active=False)
		db.add(employee)
		db.commit()

	resp = client.get(
		"/employees",
		params={"is_active": False, "search": "Inactive Target"},
		headers={"Authorization": f"Bearer {access}"},
	)
	assert resp.status_code == 200, resp.text
	data = resp.json()
	assert data["total"] == 1
	assert data["items"][0]["is_active"] is False


# GET /employees/{id} с ролью admin → 200
def test_get_employee_by_id_as_admin_is_200(client, admin_tokens: dict, admin_user, db):
	access = admin_tokens["access_token"]
	admin_employee = db.query(Employee).filter(Employee.user_id == admin_user.id).first()

	resp = client.get(f"/employees/{admin_employee.id}", headers={"Authorization": f"Bearer {access}"})
	assert resp.status_code == 200, resp.text
	assert resp.json()["email"] == admin_employee.email


# GET /employees/{id} для несуществующего id → 404
def test_get_employee_by_id_not_found_is_404(client, admin_tokens: dict):
	access = admin_tokens["access_token"]
	resp = client.get("/employees/999999", headers={"Authorization": f"Bearer {access}"})
	assert resp.status_code == 404


# GET /employees/positions с ролью hr/admin → список без дублей и None
def test_list_positions_as_admin_is_200(client, admin_tokens: dict, db):
	access = admin_tokens["access_token"]
	employee = db.query(Employee).filter(Employee.email == "positions_target@crm.com").first()
	if not employee:
		employee = Employee(full_name="Positions Target", email="positions_target@crm.com", position="QA Engineer", is_active=True)
		db.add(employee)
		db.commit()

	resp = client.get("/employees/positions", headers={"Authorization": f"Bearer {access}"})
	assert resp.status_code == 200, resp.text
	assert "QA Engineer" in resp.json()
	assert None not in resp.json()


# GET /employees/me без привязанного Employee → 404
def test_get_my_employee_without_link_is_404(client, plain_user_tokens: dict):
	access = plain_user_tokens["access_token"]
	resp = client.get("/employees/me", headers={"Authorization": f"Bearer {access}"})
	assert resp.status_code == 404


# GET /employees/me с привязанным Employee → 200
def test_get_my_employee_as_admin_is_200(client, admin_tokens: dict, admin_user, db):
	access = admin_tokens["access_token"]
	resp = client.get("/employees/me", headers={"Authorization": f"Bearer {access}"})
	assert resp.status_code == 200, resp.text
	assert resp.json()["user_id"] == admin_user.id


# PATCH /employees/me обновляет только phone/telegram
def test_patch_my_employee_updates_phone_and_telegram(client, admin_tokens: dict, admin_user, db):
	access = admin_tokens["access_token"]
	resp = client.patch(
		"/employees/me",
		json={"phone": "+7 900 123-45-67", "telegram": "@test_admin"},
		headers={"Authorization": f"Bearer {access}"},
	)
	assert resp.status_code == 200, resp.text
	data = resp.json()
	assert data["phone"] == "+7 900 123-45-67"
	assert data["telegram"] == "@test_admin"

	# не даёт менять чужие/привилегированные поля через self-update схему
	resp = client.patch(
		"/employees/me",
		json={"phone": "+7 900 000-00-00", "full_name": "Hacked Name"},
		headers={"Authorization": f"Bearer {access}"},
	)
	assert resp.status_code == 200, resp.text
	assert resp.json()["full_name"] != "Hacked Name"


# PATCH /employees/me без привязанного Employee → 404
def test_patch_my_employee_without_link_is_404(client, plain_user_tokens: dict):
	access = plain_user_tokens["access_token"]
	resp = client.patch(
		"/employees/me",
		json={"phone": "+7 900 000-00-00"},
		headers={"Authorization": f"Bearer {access}"},
	)
	assert resp.status_code == 404
