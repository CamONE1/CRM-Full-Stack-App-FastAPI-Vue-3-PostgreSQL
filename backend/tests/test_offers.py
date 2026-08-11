from datetime import datetime, timedelta, timezone

from app.offers.models import Offer


def _auth(tokens: dict) -> dict:
	return {"Authorization": f"Bearer {tokens['access_token']}"}


def _create_draft(client, admin_tokens: dict, **overrides) -> dict:
	payload = {
		"candidate_name": "Ivan Petrov",
		"candidate_email": "ivan.petrov@example.com",
		"position": "Backend Developer",
		"salary_note": "200 000 RUB gross",
	}
	payload.update(overrides)
	resp = client.post("/offers", json=payload, headers=_auth(admin_tokens))
	assert resp.status_code == 201, resp.text
	return resp.json()


def _send(client, admin_tokens: dict, offer_id: int):
	return client.post(f"/offers/{offer_id}/send", headers=_auth(admin_tokens))


# GET /offers без токена → 401
def test_list_offers_without_token_is_401(client):
	resp = client.get("/offers")
	assert resp.status_code == 401


# GET /offers с ролью user (не hr/admin) → 403
def test_list_offers_as_plain_user_is_403(client, plain_user_tokens: dict):
	resp = client.get("/offers", headers=_auth(plain_user_tokens))
	assert resp.status_code == 403


# POST /offers с ролью admin → 201, статус draft, токена ещё нет
def test_create_offer_as_admin_creates_draft(client, admin_tokens: dict):
	offer = _create_draft(client, admin_tokens)
	assert offer["status"] == "draft"
	assert offer["public_token"] is None


# POST /offers/{id}/send без expires_at → 422
def test_send_offer_without_expires_at_is_422(client, admin_tokens: dict):
	offer = _create_draft(client, admin_tokens, candidate_email="no_expiry@example.com")
	resp = _send(client, admin_tokens, offer["id"])
	assert resp.status_code == 422, resp.text


# POST /offers/{id}/send с expires_at → 200, статус sent, генерируется public_token
def test_send_offer_generates_token_and_sets_sent(client, admin_tokens: dict):
	expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
	offer = _create_draft(client, admin_tokens, candidate_email="send_ok@example.com", expires_at=expires_at)
	resp = _send(client, admin_tokens, offer["id"])
	assert resp.status_code == 200, resp.text
	data = resp.json()
	assert data["status"] == "sent"
	assert data["public_token"] is not None


# Повторный send уже отправленного оффера → 409 (invalid transition)
def test_send_offer_twice_is_409(client, admin_tokens: dict):
	expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
	offer = _create_draft(client, admin_tokens, candidate_email="send_twice@example.com", expires_at=expires_at)
	_send(client, admin_tokens, offer["id"])
	resp = _send(client, admin_tokens, offer["id"])
	assert resp.status_code == 409, resp.text


# PATCH оффера после отправки (не draft) → 409
def test_patch_offer_after_sent_is_409(client, admin_tokens: dict):
	expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
	offer = _create_draft(client, admin_tokens, candidate_email="patch_after_sent@example.com", expires_at=expires_at)
	_send(client, admin_tokens, offer["id"])
	resp = client.patch(f"/offers/{offer['id']}", json={"position": "Senior Backend"}, headers=_auth(admin_tokens))
	assert resp.status_code == 409, resp.text


# GET /public/offers/{token} возвращает только урезанную схему, без внутренних полей
def test_public_get_offer_returns_restricted_schema(client, admin_tokens: dict):
	expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
	offer = _create_draft(client, admin_tokens, candidate_email="public_schema@example.com", expires_at=expires_at)
	sent = _send(client, admin_tokens, offer["id"]).json()

	resp = client.get(f"/public/offers/{sent['public_token']}")
	assert resp.status_code == 200, resp.text
	data = resp.json()
	assert set(data.keys()) == {
		"candidate_name",
		"position",
		"salary_note",
		"status",
		"expires_at",
		"responded_at",
	}


# GET /public/offers/{token} с неизвестным токеном → 404
def test_public_get_offer_unknown_token_is_404(client):
	resp = client.get("/public/offers/00000000-0000-0000-0000-000000000000")
	assert resp.status_code == 404


# Повторный accept — идемпотентен (200, без ошибки)
def test_respond_accept_then_repeat_accept_is_idempotent(client, admin_tokens: dict):
	expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
	offer = _create_draft(client, admin_tokens, candidate_email="idempotent_accept@example.com", expires_at=expires_at)
	sent = _send(client, admin_tokens, offer["id"]).json()
	token = sent["public_token"]

	first = client.post(f"/public/offers/{token}/respond", json={"action": "accept"})
	assert first.status_code == 200, first.text
	assert first.json()["status"] == "accepted"

	second = client.post(f"/public/offers/{token}/respond", json={"action": "accept"})
	assert second.status_code == 200, second.text
	assert second.json()["status"] == "accepted"


# decline после accept — противоположное действие на terminal-статусе → 409
def test_respond_decline_after_accept_is_409(client, admin_tokens: dict):
	expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
	offer = _create_draft(client, admin_tokens, candidate_email="opposite_action@example.com", expires_at=expires_at)
	sent = _send(client, admin_tokens, offer["id"]).json()
	token = sent["public_token"]

	client.post(f"/public/offers/{token}/respond", json={"action": "accept"})
	resp = client.post(f"/public/offers/{token}/respond", json={"action": "decline"})
	assert resp.status_code == 409, resp.text


# Ответ на просроченный оффер (expires_at в прошлом, статус лениво стал expired) → 409
def test_respond_on_expired_offer_is_409(client, admin_tokens: dict, db):
	expires_at = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
	offer = _create_draft(client, admin_tokens, candidate_email="expired_offer@example.com", expires_at=expires_at)
	sent = _send(client, admin_tokens, offer["id"]).json()
	token = sent["public_token"]

	# GET триггерит ленивую проверку expires_at и переводит статус в expired
	get_resp = client.get(f"/public/offers/{token}")
	assert get_resp.json()["status"] == "expired"

	respond_resp = client.post(f"/public/offers/{token}/respond", json={"action": "accept"})
	assert respond_resp.status_code == 409, respond_resp.text

	db_offer = db.query(Offer).filter(Offer.public_token == token).first()
	assert db_offer.status == "expired"


# GET /offers по умолчанию скрывает архивные, include_archived=true — показывает
def test_list_offers_hides_archived_by_default(client, admin_tokens: dict, db):
	# На случай повторного прогона против той же dev-БД: без выделенной тестовой
	# БД предыдущие запуски могли оставить офферы с этим email.
	db.query(Offer).filter(Offer.candidate_email == "archived_target@example.com").delete()
	db.commit()

	offer = _create_draft(client, admin_tokens, candidate_email="archived_target@example.com")
	client.post(f"/offers/{offer['id']}/archive", headers=_auth(admin_tokens))

	default_resp = client.get(
		"/offers", params={"search": "archived_target"}, headers=_auth(admin_tokens)
	)
	assert default_resp.json()["total"] == 0

	with_archived_resp = client.get(
		"/offers",
		params={"search": "archived_target", "include_archived": True},
		headers=_auth(admin_tokens),
	)
	assert with_archived_resp.json()["total"] == 1
	assert with_archived_resp.json()["items"][0]["is_archived"] is True


# Повторная архивация — идемпотентна, archived_at не меняется
def test_archive_offer_is_idempotent(client, admin_tokens: dict):
	offer = _create_draft(client, admin_tokens, candidate_email="archive_twice@example.com")
	first = client.post(f"/offers/{offer['id']}/archive", headers=_auth(admin_tokens))
	assert first.status_code == 200, first.text
	archived_at = first.json()["archived_at"]

	second = client.post(f"/offers/{offer['id']}/archive", headers=_auth(admin_tokens))
	assert second.status_code == 200, second.text
	assert second.json()["archived_at"] == archived_at
