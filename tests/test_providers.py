def _admin(client):
    r = client.post(
        "/auths/signup",
        json={"email": "prov@t.com", "name": "P", "password": "pass1234!"},
    )
    return r.json()["token"]  # first signup = admin


def _nonadmin(client):
    client.post(
        "/auths/signup",
        json={"email": "a0@t.com", "name": "A0", "password": "pass1234!"},
    )  # admin
    r = client.post(
        "/auths/signup",
        json={"email": "plain@t.com", "name": "P", "password": "pass1234!"},
    )
    return r.json()["token"]


def _auth(t):
    return {"Authorization": f"Bearer {t}"}


def test_list_providers(client):
    r = client.get("/api/v1/providers/", headers=_auth(_admin(client)))
    assert r.status_code == 200
    ids = {p["id"] for p in r.json()}
    assert {"openai", "ollama"} <= ids


def test_openai_config_shape(client):
    r = client.get("/api/v1/providers/openai/config", headers=_auth(_admin(client)))
    assert r.status_code == 200
    cfg = r.json()
    assert "ENABLE_OPENAI_API" in cfg
    assert "OPENAI_API_BASE_URLS" in cfg
    assert "OPENAI_API_KEYS" in cfg
    assert "OPENAI_API_CONFIGS" in cfg


def test_openai_config_update_persists(client):
    token = _admin(client)
    client.post(
        "/api/v1/providers/openai/config/update",
        json={
            "ENABLE_OPENAI_API": True,
            "OPENAI_API_BASE_URLS": ["https://api.openai.com/v1"],
            "OPENAI_API_KEYS": ["sk-abc"],
            "OPENAI_API_CONFIGS": {},
        },
        headers=_auth(token),
    )
    r = client.get("/api/v1/providers/openai/config", headers=_auth(token))
    assert r.json()["OPENAI_API_KEYS"] == ["sk-abc"]


def test_openai_urls_roundtrip(client):
    token = _admin(client)
    client.post(
        "/api/v1/providers/openai/urls/update",
        json={"urls": ["https://x/v1", "https://y/v1"]},
        headers=_auth(token),
    )
    r = client.get("/api/v1/providers/openai/urls", headers=_auth(token))
    assert r.json()["OPENAI_API_BASE_URLS"] == ["https://x/v1", "https://y/v1"]


def test_openai_keys_roundtrip_real_values(client):
    token = _admin(client)
    client.post(
        "/api/v1/providers/openai/keys/update",
        json={"keys": ["sk-realsecret123"]},
        headers=_auth(token),
    )
    r = client.get("/api/v1/providers/openai/keys", headers=_auth(token))
    # admin gets REAL key values (settings page needs them) — no masking
    assert r.json()["OPENAI_API_KEYS"] == ["sk-realsecret123"]


def test_ollama_config_shape(client):
    r = client.get("/api/v1/providers/ollama/config", headers=_auth(_admin(client)))
    assert r.status_code == 200
    cfg = r.json()
    assert "ENABLE_OLLAMA_API" in cfg
    assert "OLLAMA_BASE_URLS" in cfg
    assert "OLLAMA_API_CONFIGS" in cfg


def test_ollama_urls_roundtrip(client):
    token = _admin(client)
    client.post(
        "/api/v1/providers/ollama/urls/update",
        json={"urls": ["http://h1:11434"]},
        headers=_auth(token),
    )
    r = client.get("/api/v1/providers/ollama/urls", headers=_auth(token))
    assert r.json()["OLLAMA_BASE_URLS"] == ["http://h1:11434"]


def test_openai_verify_unreachable(client):
    token = _admin(client)
    r = client.post(
        "/api/v1/providers/openai/verify",
        json={"url": "http://127.0.0.1:1/v1", "key": "sk-x"},
        headers=_auth(token),
    )
    assert r.status_code == 200
    assert r.json()["status"] in ("unreachable", "error")


def test_non_admin_cannot_read_openai_config(client):
    attacker = _nonadmin(client)
    r = client.get("/api/v1/providers/openai/config", headers=_auth(attacker))
    assert r.status_code == 403


def test_non_admin_cannot_list_providers(client):
    attacker = _nonadmin(client)
    r = client.get("/api/v1/providers/", headers=_auth(attacker))
    assert r.status_code == 403


def test_ollama_verify_unreachable(client):
    token = _admin(client)
    r = client.post(
        "/api/v1/providers/ollama/verify",
        json={"url": "http://127.0.0.1:1", "key": ""},
        headers=_auth(token),
    )
    assert r.status_code == 200
    assert r.json()["status"] in ("unreachable", "error")


def test_config_persists_across_service_instances(client):
    # AppConfig-backed: a fresh request (new ProvidersService) still sees the value
    token = _admin(client)
    client.post(
        "/api/v1/providers/ollama/config/update",
        json={
            "ENABLE_OLLAMA_API": False,
            "OLLAMA_BASE_URLS": ["http://z:11434"],
            "OLLAMA_API_CONFIGS": {},
        },
        headers=_auth(token),
    )
    r = client.get("/api/v1/providers/ollama/config", headers=_auth(token))
    assert r.json()["ENABLE_OLLAMA_API"] is False
    assert r.json()["OLLAMA_BASE_URLS"] == ["http://z:11434"]


def test_openai_models_disabled(client):
    """If ENABLE_OPENAI_API is False, models returns 503."""
    token = _admin(client)
    client.post(
        "/api/v1/providers/openai/config/update",
        json={
            "ENABLE_OPENAI_API": False,
            "OPENAI_API_BASE_URLS": [],
            "OPENAI_API_KEYS": [],
            "OPENAI_API_CONFIGS": {},
        },
        headers=_auth(token),
    )
    r = client.get("/api/v1/providers/openai/models", headers=_auth(token))
    assert r.status_code == 503


def test_openai_models_returns_list_shape(client):
    """With unreachable URL, returns empty list (skips bad upstream)."""
    token = _admin(client)
    client.post(
        "/api/v1/providers/openai/config/update",
        json={
            "ENABLE_OPENAI_API": True,
            "OPENAI_API_BASE_URLS": ["http://127.0.0.1:1/v1"],
            "OPENAI_API_KEYS": ["sk-x"],
            "OPENAI_API_CONFIGS": {},
        },
        headers=_auth(token),
    )
    r = client.get("/api/v1/providers/openai/models", headers=_auth(token))
    assert r.status_code == 200
    assert "data" in r.json()
    assert isinstance(r.json()["data"], list)


def test_openai_models_by_idx_out_of_range(client):
    token = _admin(client)
    client.post(
        "/api/v1/providers/openai/config/update",
        json={
            "ENABLE_OPENAI_API": True,
            "OPENAI_API_BASE_URLS": ["http://127.0.0.1:1/v1"],
            "OPENAI_API_KEYS": [],
            "OPENAI_API_CONFIGS": {},
        },
        headers=_auth(token),
    )
    r = client.get("/api/v1/providers/openai/models/99", headers=_auth(token))
    assert r.status_code == 404


def test_openai_chat_completions_disabled(client):
    token = _admin(client)
    client.post(
        "/api/v1/providers/openai/config/update",
        json={
            "ENABLE_OPENAI_API": False,
            "OPENAI_API_BASE_URLS": [],
            "OPENAI_API_KEYS": [],
            "OPENAI_API_CONFIGS": {},
        },
        headers=_auth(token),
    )
    r = client.post(
        "/api/v1/providers/openai/chat/completions",
        json={"model": "gpt-4", "messages": []},
        headers=_auth(token),
    )
    assert r.status_code == 503


def test_non_admin_can_access_chat_completions(client):
    """Proxy endpoints are non-admin — any authenticated user can call them."""
    nonadmin_token = _nonadmin(
        client
    )  # creates admin (a0@t.com) + plain user (plain@t.com)
    admin_token = client.post(
        "/auths/signin", json={"email": "a0@t.com", "password": "pass1234!"}
    ).json()["token"]
    client.post(
        "/api/v1/providers/openai/config/update",
        json={
            "ENABLE_OPENAI_API": True,
            "OPENAI_API_BASE_URLS": ["http://127.0.0.1:1/v1"],
            "OPENAI_API_KEYS": [],
            "OPENAI_API_CONFIGS": {},
        },
        headers=_auth(admin_token),
    )
    r = client.post(
        "/api/v1/providers/openai/chat/completions",
        json={"model": "gpt-4", "messages": []},
        headers=_auth(nonadmin_token),
    )
    # 502 (unreachable upstream) — NOT 403
    assert r.status_code != 403


def test_chat_completions_routes_by_model(client):
    """chat/completions uses model→urlIdx cache to route to the correct upstream."""
    token = _admin(client)
    client.post(
        "/api/v1/providers/openai/config/update",
        json={
            "ENABLE_OPENAI_API": True,
            "OPENAI_API_BASE_URLS": ["http://127.0.0.1:1/v1", "http://127.0.0.1:2/v1"],
            "OPENAI_API_KEYS": ["sk-a", "sk-b"],
            "OPENAI_API_CONFIGS": {},
        },
        headers=_auth(token),
    )
    r = client.post(
        "/api/v1/providers/openai/chat/completions",
        json={"model": "unknown-model", "messages": []},
        headers=_auth(token),
    )
    # "unknown-model" not in cache → falls back to index 0 → 502 (unreachable)
    assert r.status_code == 502


def test_openai_audio_speech_disabled(client):
    token = _admin(client)
    client.post(
        "/api/v1/providers/openai/config/update",
        json={
            "ENABLE_OPENAI_API": False,
            "OPENAI_API_BASE_URLS": [],
            "OPENAI_API_KEYS": [],
            "OPENAI_API_CONFIGS": {},
        },
        headers=_auth(token),
    )
    r = client.post(
        "/api/v1/providers/openai/audio/speech",
        json={"model": "tts-1", "input": "hello", "voice": "alloy"},
        headers=_auth(token),
    )
    assert r.status_code == 503


def test_openai_audio_speech_unreachable(client):
    token = _admin(client)
    client.post(
        "/api/v1/providers/openai/config/update",
        json={
            "ENABLE_OPENAI_API": True,
            "OPENAI_API_BASE_URLS": ["http://127.0.0.1:1/v1"],
            "OPENAI_API_KEYS": ["sk-x"],
            "OPENAI_API_CONFIGS": {},
        },
        headers=_auth(token),
    )
    r = client.post(
        "/api/v1/providers/openai/audio/speech",
        json={"model": "tts-1", "input": "hello", "voice": "alloy"},
        headers=_auth(token),
    )
    assert r.status_code == 502


def test_proxy_stream_upstream_error_returns_non_200(client):
    """proxy_stream must not return 200 when upstream is unreachable (eager connect)."""
    token = _admin(client)
    client.post(
        "/api/v1/providers/openai/config/update",
        json={
            "ENABLE_OPENAI_API": True,
            "OPENAI_API_BASE_URLS": ["http://127.0.0.1:1/v1"],
            "OPENAI_API_KEYS": ["sk-x"],
            "OPENAI_API_CONFIGS": {},
        },
        headers=_auth(token),
    )
    r = client.post(
        "/api/v1/providers/openai/chat/completions",
        json={"model": "gpt-4", "messages": [], "stream": True},
        headers=_auth(token),
    )
    # Must NOT be 200 — upstream is unreachable so we expect 502
    assert r.status_code != 200
    assert r.status_code == 502


# ── Ollama discovery + chat tests ─────────────────────────────────────────────


def _setup_ollama(client, token, urls=None, enabled=True):
    client.post(
        "/api/v1/providers/ollama/config/update",
        json={
            "ENABLE_OLLAMA_API": enabled,
            "OLLAMA_BASE_URLS": urls or ["http://127.0.0.1:11434"],
            "OLLAMA_API_CONFIGS": {},
        },
        headers=_auth(token),
    )


def test_ollama_api_version_disabled(client):
    token = _admin(client)
    _setup_ollama(client, token, enabled=False)
    r = client.get("/api/v1/providers/ollama/api/version", headers=_auth(token))
    assert r.status_code == 200
    assert r.json()["version"] is False


def test_ollama_api_version_unreachable(client):
    token = _admin(client)
    _setup_ollama(client, token, urls=["http://127.0.0.1:1"])
    r = client.get("/api/v1/providers/ollama/api/version", headers=_auth(token))
    assert r.status_code == 503  # no backends reachable


def test_ollama_api_version_by_idx_out_of_range(client):
    token = _admin(client)
    _setup_ollama(client, token, urls=["http://127.0.0.1:1"])
    r = client.get("/api/v1/providers/ollama/api/version/99", headers=_auth(token))
    assert r.status_code == 404


def test_ollama_api_tags_disabled(client):
    token = _admin(client)
    _setup_ollama(client, token, enabled=False)
    r = client.get("/api/v1/providers/ollama/api/tags", headers=_auth(token))
    assert r.status_code == 200
    assert r.json() == {"models": []}


def test_ollama_api_tags_unreachable_returns_empty(client):
    token = _admin(client)
    _setup_ollama(client, token, urls=["http://127.0.0.1:1"])
    r = client.get("/api/v1/providers/ollama/api/tags", headers=_auth(token))
    assert r.status_code == 200
    assert r.json() == {"models": []}  # skips unreachable, returns empty


def test_ollama_api_chat_disabled(client):
    token = _admin(client)
    _setup_ollama(client, token, enabled=False)
    r = client.post(
        "/api/v1/providers/ollama/api/chat",
        json={"model": "llama3", "messages": []},
        headers=_auth(token),
    )
    assert r.status_code == 503


def test_ollama_api_chat_unreachable(client):
    token = _admin(client)
    _setup_ollama(client, token, urls=["http://127.0.0.1:1"])
    r = client.post(
        "/api/v1/providers/ollama/api/chat",
        json={"model": "llama3", "messages": [], "stream": False},
        headers=_auth(token),
    )
    assert r.status_code == 502


def test_ollama_embeddings_disabled(client):
    token = _admin(client)
    _setup_ollama(client, token, enabled=False)
    r = client.post(
        "/api/v1/providers/ollama/api/embeddings",
        json={"model": "llama3", "prompt": "hi"},
        headers=_auth(token),
    )
    assert r.status_code == 503


def test_ollama_generate_disabled(client):
    token = _admin(client)
    _setup_ollama(client, token, enabled=False)
    r = client.post(
        "/api/v1/providers/ollama/api/generate",
        json={"model": "llama3", "prompt": "hi"},
        headers=_auth(token),
    )
    assert r.status_code == 503


# ── Ollama model management tests ─────────────────────────────────────────────


def test_ollama_pull_admin_only(client):
    nonadmin = _nonadmin(client)
    r = client.post(
        "/api/v1/providers/ollama/api/pull",
        json={"model": "llama3"},
        headers=_auth(nonadmin),
    )
    assert r.status_code == 403


def test_ollama_pull_disabled(client):
    token = _admin(client)
    _setup_ollama(client, token, enabled=False)
    r = client.post(
        "/api/v1/providers/ollama/api/pull",
        json={"model": "llama3"},
        headers=_auth(token),
    )
    assert r.status_code == 503


def test_ollama_create_admin_only(client):
    nonadmin = _nonadmin(client)
    r = client.post(
        "/api/v1/providers/ollama/api/create",
        json={"model": "mymodel", "modelfile": "FROM llama3"},
        headers=_auth(nonadmin),
    )
    assert r.status_code == 403


def test_ollama_delete_admin_only(client):
    nonadmin = _nonadmin(client)
    r = client.request(
        "DELETE",
        "/api/v1/providers/ollama/api/delete",
        json={"model": "llama3"},
        headers=_auth(nonadmin),
    )
    assert r.status_code == 403


def test_ollama_delete_missing_model_name(client):
    token = _admin(client)
    _setup_ollama(client, token, urls=["http://127.0.0.1:11434"])
    r = client.request(
        "DELETE", "/api/v1/providers/ollama/api/delete", json={}, headers=_auth(token)
    )
    assert r.status_code == 400


def test_ollama_download_invalid_host(client):
    token = _admin(client)
    _setup_ollama(client, token, urls=["http://127.0.0.1:11434"])
    r = client.post(
        "/api/v1/providers/ollama/models/download",
        json={"url": "https://evil.com/model.gguf"},
        headers=_auth(token),
    )
    assert r.status_code == 400


def test_ollama_download_admin_only(client):
    nonadmin = _nonadmin(client)
    r = client.post(
        "/api/v1/providers/ollama/models/download",
        json={"url": "https://huggingface.co/model.gguf"},
        headers=_auth(nonadmin),
    )
    assert r.status_code == 403
