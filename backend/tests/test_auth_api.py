from app.authentication.jwt_handler import create_access_token, decode_access_token


def test_register_returns_created_user(client):
    res = client.post("/auth/register", json={"email": "new@example.com", "password": "testpass123"})

    assert res.status_code == 201
    assert res.json()["email"] == "new@example.com"
    assert "hashed_password" not in res.json()


def test_register_rejects_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "testpass123"})

    res = client.post("/auth/register", json={"email": "dup@example.com", "password": "testpass123"})

    assert res.status_code == 400
    assert "already registered" in res.json()["detail"]


def test_register_rejects_short_password(client):
    res = client.post("/auth/register", json={"email": "short@example.com", "password": "short"})

    assert res.status_code == 422


def test_login_returns_bearer_token(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "testpass123"})

    res = client.post("/auth/login", data={"username": "login@example.com", "password": "testpass123"})

    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"
    assert decode_access_token(res.json()["access_token"])["sub"] is not None


def test_login_rejects_wrong_password(client):
    client.post("/auth/register", json={"email": "wrong@example.com", "password": "testpass123"})

    res = client.post("/auth/login", data={"username": "wrong@example.com", "password": "nottherightone"})

    assert res.status_code == 401
    assert res.json()["detail"] == "Incorrect email or password"


def test_login_rejects_unknown_email(client):
    res = client.post("/auth/login", data={"username": "ghost@example.com", "password": "testpass123"})

    assert res.status_code == 401


def test_protected_route_rejects_malformed_token(client):
    res = client.get("/chat/sessions", headers={"Authorization": "Bearer not-a-jwt"})

    assert res.status_code == 401
    assert res.json()["detail"] == "Could not validate credentials"


def test_protected_route_rejects_token_without_subject(client):
    token = create_access_token({"role": "admin"})

    res = client.get("/chat/sessions", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 401


def test_protected_route_rejects_token_for_deleted_user(client):
    token = create_access_token({"sub": "4242"})

    res = client.get("/chat/sessions", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 401


def test_decode_access_token_returns_none_for_invalid_token():
    assert decode_access_token("garbage.token.value") is None


def test_health_check(client):
    assert client.get("/health").json() == {"status": "ok"}
