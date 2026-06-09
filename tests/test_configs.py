def _token(client):
    r = client.post(
        "/auths/signup",
        json={"email": "cfg@t.com", "name": "C", "password": "pass1234!"},
    )
    return r.json()["token"]


def _auth(t):
    return {"Authorization": f"Bearer {t}"}


def test_get_models_config(client):
    r = client.get("/api/v1/configs/models", headers=_auth(_token(client)))
    assert r.status_code == 200


def test_get_banners_config(client):
    r = client.get("/api/v1/configs/banners", headers=_auth(_token(client)))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_suggestions(client):
    r = client.get("/api/v1/configs/suggestions", headers=_auth(_token(client)))
    assert r.status_code == 200


def test_export_config(client):
    r = client.get("/api/v1/configs/export", headers=_auth(_token(client)))
    assert r.status_code == 200


def test_import_config(client):
    token = _token(client)
    r = client.post(
        "/api/v1/configs/import",
        json={"banners": [], "suggestions": []},
        headers=_auth(token),
    )
    assert r.status_code == 200


def _nonadmin_token(client):
    client.post(
        "/auths/signup",
        json={"email": "admin0@t.com", "name": "A0", "password": "pass1234!"},
    )  # first = admin
    r = client.post(
        "/auths/signup",
        json={"email": "plain@t.com", "name": "P", "password": "pass1234!"},
    )
    return r.json()["token"]


def test_set_and_get_roundtrip(client):
    token = _token(client)  # first signup = admin
    client.post(
        "/api/v1/configs/banners",
        json=[{"id": "b1", "content": "hi"}],
        headers=_auth(token),
    )
    r = client.get("/api/v1/configs/banners", headers=_auth(token))
    assert r.status_code == 200
    assert r.json() == [{"id": "b1", "content": "hi"}]


def test_non_admin_cannot_write_banners(client):
    token = _nonadmin_token(client)
    r = client.post("/api/v1/configs/banners", json=[], headers=_auth(token))
    assert r.status_code == 403


def test_import_ignores_unknown_keys(client):
    token = _token(client)  # admin
    r = client.post(
        "/api/v1/configs/import",
        json={"banners": [], "bogus_key": "x"},
        headers=_auth(token),
    )
    assert r.status_code == 200
    assert "bogus_key" not in r.json()
