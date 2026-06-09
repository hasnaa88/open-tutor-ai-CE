def test_get_version(client):
    r = client.get("/api/v1/platform/version")
    assert r.status_code == 200
    data = r.json()
    assert "version" in data
    assert "name" in data
    assert "build_hash" in data


def test_get_changelog(client):
    r = client.get("/api/v1/platform/changelog")
    assert r.status_code == 200
    assert isinstance(r.text, str)


def test_get_banners(client):
    r = client.get("/api/v1/platform/banners")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
