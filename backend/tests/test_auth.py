def test_register_creates_user_and_returns_tokens(client):
    resp = client.post("/api/auth/register", json={
        "full_name": "Alice", "email": "alice@example.com", "password": "supersecret1",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["user"]["email"] == "alice@example.com"
    assert body["user"]["role"] == "USER"
    assert "access_token" in body and "refresh_token" in body


def test_register_duplicate_email_rejected(client):
    payload = {"full_name": "Bob", "email": "bob@example.com", "password": "supersecret1"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/api/auth/register", json={"full_name": "Carl", "email": "carl@example.com", "password": "supersecret1"})
    resp = client.post("/api/auth/login", json={"email": "carl@example.com", "password": "supersecret1"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password_rejected(client):
    client.post("/api/auth/register", json={"full_name": "Dana", "email": "dana@example.com", "password": "supersecret1"})
    resp = client.post("/api/auth/login", json={"email": "dana@example.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_valid_token(client, auth_headers, registered_user):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == registered_user["user"]["email"]


def test_protected_route_rejects_garbage_token(client):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401
