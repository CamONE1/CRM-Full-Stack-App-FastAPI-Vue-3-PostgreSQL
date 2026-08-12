from datetime import datetime, timedelta, timezone

from app.employees.models import Employee
from app.offers.models import Offer
from app.stats.service import OFFER_STATUSES


def _auth(tokens: dict) -> dict:
	return {"Authorization": f"Bearer {tokens['access_token']}"}


def _create_draft(client, admin_tokens: dict, **overrides) -> dict:
	payload = {
		"candidate_name": "Stats Candidate",
		"candidate_email": "stats_candidate@example.com",
		"position": "Backend Developer",
	}
	payload.update(overrides)
	resp = client.post("/offers", json=payload, headers=_auth(admin_tokens))
	assert resp.status_code == 201, resp.text
	return resp.json()


# GET /stats без токена → 401
def test_get_stats_without_token_is_401(client):
	resp = client.get("/stats")
	assert resp.status_code == 401


# GET /stats с ролью user (не hr/admin) → 403
def test_get_stats_as_plain_user_is_403(client, plain_user_tokens: dict):
	resp = client.get("/stats", headers=_auth(plain_user_tokens))
	assert resp.status_code == 403


# GET /stats с ролью admin → 200, ожидаемая структура (все 5 статусов офферов присутствуют)
def test_get_stats_as_admin_has_expected_shape(client, admin_tokens: dict):
	resp = client.get("/stats", headers=_auth(admin_tokens))
	assert resp.status_code == 200, resp.text
	data = resp.json()

	assert set(data["offers"]["by_status"].keys()) == set(OFFER_STATUSES)
	assert data["offers"]["total"] == sum(data["offers"]["by_status"].values())

	employees = data["employees"]
	assert employees["total"] == employees["active"] + employees["inactive"]
	assert sum(employees["by_department"].values()) == employees["total"]

	assert len(data["recent_offers"]) <= 5
	assert len(data["recent_news"]) <= 5


# Новый draft-оффер увеличивает offers.by_status.draft и offers.total ровно на 1
def test_stats_offers_by_status_reflects_new_draft(client, admin_tokens: dict, db):
	db.query(Offer).filter(Offer.candidate_email == "stats_new_draft@example.com").delete()
	db.commit()

	before = client.get("/stats", headers=_auth(admin_tokens)).json()["offers"]

	_create_draft(client, admin_tokens, candidate_email="stats_new_draft@example.com")

	after = client.get("/stats", headers=_auth(admin_tokens)).json()["offers"]
	assert after["by_status"]["draft"] == before["by_status"]["draft"] + 1
	assert after["total"] == before["total"] + 1


# Архивный оффер не участвует в воронке: после архивации счётчик статуса и total откатываются
def test_stats_excludes_archived_offers(client, admin_tokens: dict, db):
	db.query(Offer).filter(Offer.candidate_email == "stats_archived@example.com").delete()
	db.commit()

	baseline = client.get("/stats", headers=_auth(admin_tokens)).json()["offers"]

	offer = _create_draft(client, admin_tokens, candidate_email="stats_archived@example.com")
	with_offer = client.get("/stats", headers=_auth(admin_tokens)).json()["offers"]
	assert with_offer["by_status"]["draft"] == baseline["by_status"]["draft"] + 1

	client.post(f"/offers/{offer['id']}/archive", headers=_auth(admin_tokens))
	after_archive = client.get("/stats", headers=_auth(admin_tokens)).json()["offers"]
	assert after_archive["by_status"]["draft"] == baseline["by_status"]["draft"]
	assert after_archive["total"] == baseline["total"]


# GET /stats сама резолвит просроченные 'sent' офферы в 'expired' (bulk, не только по индивидуальному чтению)
def test_stats_resolves_due_sent_offers_to_expired(client, admin_tokens: dict, db):
	db.query(Offer).filter(Offer.candidate_email == "stats_expired@example.com").delete()
	db.commit()

	expires_at = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
	offer = _create_draft(client, admin_tokens, candidate_email="stats_expired@example.com", expires_at=expires_at)
	send_resp = client.post(f"/offers/{offer['id']}/send", headers=_auth(admin_tokens))
	assert send_resp.json()["status"] == "sent"

	# Никто ещё не читал этот оффер по отдельности — ленивый резолвер offers/service.py
	# не срабатывал. GET /stats обязан резолвить его сам, до агрегации.
	stats_resp = client.get("/stats", headers=_auth(admin_tokens))
	assert stats_resp.status_code == 200, stats_resp.text

	db.expire_all()
	db_offer = db.query(Offer).filter(Offer.candidate_email == "stats_expired@example.com").first()
	assert db_offer.status == "expired"


# Сотрудник без department попадает в бакет "Без отдела", employees.total учитывает всех
def test_stats_employees_department_bucket_for_null_department(client, admin_tokens: dict, db):
	employee = db.query(Employee).filter(Employee.email == "stats_no_department@crm.com").first()
	if not employee:
		employee = Employee(full_name="No Department", email="stats_no_department@crm.com", is_active=True)
		db.add(employee)
		db.commit()

	resp = client.get("/stats", headers=_auth(admin_tokens))
	assert resp.status_code == 200, resp.text
	assert resp.json()["employees"]["by_department"]["Без отдела"] >= 1
