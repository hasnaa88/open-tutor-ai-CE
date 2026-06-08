"""Providers service — Hermes-style core. Config via ProviderConfigService, upstream via httpx.

No open_webui import. Ollama is treated as OpenAI-compatible via its /v1 endpoint where
possible; native Ollama API operations live in a separate adapter (later task).
"""

import logging
import time as _time
from typing import Any, Dict, List, TYPE_CHECKING

import httpx
from sqlalchemy.orm import Session

from providers.config_service import ProviderConfigService
from providers.proxy import proxy_json, resolve_ollama_url

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)

# Module-level cache — survives across request-scoped ProvidersService instances
_OPENAI_MODEL_MAP: dict = {}  # model_id → url_idx
_OPENAI_MODEL_MAP_TS: float = 0.0
_OPENAI_MODEL_MAP_TTL: float = 60.0  # seconds — matches OpenWebUI MODELS_CACHE_TTL


async def get_openai_models_map(config: "ProviderConfigService") -> dict:
    """Return {model_id: url_idx} with 60-second TTL cache.

    Mirrors OpenWebUI's app.state.OPENAI_MODELS but scoped to a module-level
    cache so it survives across request-scoped ProvidersService instances.
    """
    global _OPENAI_MODEL_MAP, _OPENAI_MODEL_MAP_TS
    now = _time.monotonic()
    if _OPENAI_MODEL_MAP and (now - _OPENAI_MODEL_MAP_TS) < _OPENAI_MODEL_MAP_TTL:
        return _OPENAI_MODEL_MAP

    cfg = config.get_openai()
    urls: list = cfg.get("OPENAI_API_BASE_URLS") or []
    keys: list = cfg.get("OPENAI_API_KEYS") or []
    result: dict = {}
    for idx, url in enumerate(urls):
        key = keys[idx] if idx < len(keys) else ""
        try:
            data = await proxy_json(url.rstrip("/"), key, "GET", "models")
            for m in data.get("data", []):
                model_id = m.get("id") or m.get("name")
                if model_id and model_id not in result:
                    result[model_id] = idx
        except Exception:
            pass  # skip unreachable upstream

    _OPENAI_MODEL_MAP = result
    _OPENAI_MODEL_MAP_TS = now
    return result


def invalidate_openai_models_cache() -> None:
    global _OPENAI_MODEL_MAP_TS
    _OPENAI_MODEL_MAP_TS = 0.0


_OLLAMA_MODEL_MAP: dict = {}  # model_name → url_idx
_OLLAMA_MODEL_MAP_TS: float = 0.0
_OLLAMA_MODEL_MAP_TTL: float = 60.0


async def get_ollama_models_map(config: "ProviderConfigService") -> dict:
    """Return {model_name: url_idx} with 60s TTL cache from /api/tags aggregation."""
    global _OLLAMA_MODEL_MAP, _OLLAMA_MODEL_MAP_TS
    now = _time.monotonic()
    if _OLLAMA_MODEL_MAP and (now - _OLLAMA_MODEL_MAP_TS) < _OLLAMA_MODEL_MAP_TTL:
        return _OLLAMA_MODEL_MAP

    cfg = config.get_ollama()
    urls: list = cfg.get("OLLAMA_BASE_URLS") or []
    result: dict = {}
    for idx, url in enumerate(urls):
        try:
            data = await proxy_json(url.rstrip("/"), "", "GET", "api/tags")
            for m in data.get("models", []):
                name = m.get("model") or m.get("name")
                if name and name not in result:
                    result[name] = idx
        except Exception:
            pass

    _OLLAMA_MODEL_MAP = result
    _OLLAMA_MODEL_MAP_TS = now
    return result


def invalidate_ollama_models_cache() -> None:
    global _OLLAMA_MODEL_MAP_TS
    _OLLAMA_MODEL_MAP_TS = 0.0


class ProvidersService:
    def __init__(self, session: Session):
        self.config = ProviderConfigService(session)

    def list_providers(self) -> List[dict]:
        oa = self.config.get_openai()
        ol = self.config.get_ollama()
        return [
            {
                "id": "openai",
                "name": "OpenAI-Compatible",
                "enabled": bool(oa.get("ENABLE_OPENAI_API")),
            },
            {
                "id": "ollama",
                "name": "Ollama",
                "enabled": bool(ol.get("ENABLE_OLLAMA_API")),
            },
        ]

    async def openai_models_map(self) -> dict:
        return await get_openai_models_map(self.config)

    async def ollama_models_map(self) -> dict:
        return await get_ollama_models_map(self.config)

    async def verify_openai(self, url: str, key: str) -> dict:
        """Verify an OpenAI-compatible endpoint by listing models."""
        if not url:
            return {"status": "error", "detail": "url required"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    f"{url.rstrip('/')}/models",
                    headers={"Authorization": f"Bearer {key}"} if key else {},
                )
                r.raise_for_status()
                data = r.json().get("data", [])
                return {"status": "ok", "model_count": len(data)}
        except Exception as exc:
            log.warning("OpenAI verify failed: %s", exc)
            return {"status": "unreachable", "detail": str(exc)}

    async def verify_ollama(self, url: str, key: str = "") -> dict:
        """Verify an Ollama endpoint via its native /api/version probe."""
        if not url:
            return {"status": "error", "detail": "url required"}
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(
                    f"{url.rstrip('/')}/api/version",
                    headers={"Authorization": f"Bearer {key}"} if key else {},
                )
                r.raise_for_status()
                return {"status": "ok", "version": r.json().get("version")}
        except Exception as exc:
            log.warning("Ollama verify failed: %s", exc)
            return {"status": "unreachable", "detail": str(exc)}
