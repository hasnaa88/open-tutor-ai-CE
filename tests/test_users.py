def _admin_token(client):
    r = client.post(
        "/auths/signup",
        json={"email": "admin@t.com", "name": "Admin", "password": "pass1234!"},
    )
    return r.json()["token"]


def _user_token(client, email="user@t.com"):
    r = client.post(
        "/auths/signup", json={"email": email, "name": "User", "password": "pass1234!"}
    )
    return r.json()["token"]


def _auth(t):
    return {"Authorization": f"Bearer {t}"}


def test_get_users(client):
    token = _admin_token(client)
    r = client.get("/api/v1/users/", headers=_auth(token))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_user_settings(client):
    token = _admin_token(client)
    r = client.get("/api/v1/users/user/settings", headers=_auth(token))
    assert r.status_code == 200


def test_update_user_settings(client):
    token = _admin_token(client)
    r = client.post(
        "/api/v1/users/user/settings/update",
        json={"ui": {"theme": "dark"}},
        headers=_auth(token),
    )
    assert r.status_code == 200
    assert r.json()["ui"]["theme"] == "dark"


def test_get_user_info(client):
    token = _admin_token(client)
    r = client.get("/api/v1/users/user/info", headers=_auth(token))
    assert r.status_code == 200


def test_update_user_info(client):
    token = _admin_token(client)
    r = client.post(
        "/api/v1/users/user/info/update", json={"bio": "Teacher"}, headers=_auth(token)
    )
    assert r.status_code == 200


def test_update_user_role(client):
    token = _admin_token(client)
    _user_token(client)
    users = client.get("/api/v1/users/", headers=_auth(token)).json()
    non_admin = [u for u in users if not u.get("is_admin")][0]
    r = client.post(
        "/api/v1/users/update/role",
        json={"id": non_admin["id"], "role": "admin"},
        headers=_auth(token),
    )
    assert r.status_code == 200


def test_get_user_by_id(client):
    token = _admin_token(client)
    users = client.get("/api/v1/users/", headers=_auth(token)).json()
    uid = users[0]["id"]
    r = client.get(f"/api/v1/users/{uid}", headers=_auth(token))
    assert r.status_code == 200
    assert r.json()["id"] == uid


def test_delete_user(client):
    token = _admin_token(client)
    _user_token(client, "del2@t.com")
    users = client.get("/api/v1/users/", headers=_auth(token)).json()
    victim = [u for u in users if u["email"] == "del2@t.com"][0]
    r = client.delete(f"/api/v1/users/{victim['id']}", headers=_auth(token))
    assert r.status_code == 200


def test_get_default_permissions(client):
    token = _admin_token(client)
    r = client.get("/api/v1/users/default/permissions", headers=_auth(token))
    assert r.status_code == 200


def test_non_admin_cannot_list_users(client):
    _admin_token(client)  # first signup = admin
    user_tok = _user_token(client, "plain@t.com")
    r = client.get("/api/v1/users/", headers=_auth(user_tok))
    assert r.status_code == 403


def test_cannot_delete_self(client):
    token = _admin_token(client)
    me = client.get("/api/v1/users/", headers=_auth(token)).json()[0]
    r = client.delete(f"/api/v1/users/{me['id']}", headers=_auth(token))
    assert r.status_code == 400


def test_update_nonexistent_user_returns_404(client):
    token = _admin_token(client)
    r = client.post(
        "/api/v1/users/does-not-exist/update",
        json={"name": "Ghost"},
        headers=_auth(token),
    )
    assert r.status_code == 404
