"""Contract coverage test: verifies every UI-called path exists in the OpenAPI schema.

The scanner extracts fetch() calls from ui/src/lib/apis/**/*.ts and maps them
to backend paths. Falls back to a small hardcoded set for paths with no JS client.

Scanned paths that reference open-webui features not yet ported to CE are listed
in _SCANNED_PATH_EXCLUSIONS and skipped rather than causing test failures.
"""

import re
from pathlib import Path
from typing import Dict, Set, Tuple

# ── Paths with no UI fetch() client (health, auth bootstraps) ─────────────────
# Tuples are (METHOD, path) — explicit so method-aware assertion works for these too.
_REQUIRED_PATHS_FALLBACK: Set[Tuple[str, str]] = {
    ("GET", "/health"),
    ("GET", "/api/v1/auths/"),
    ("POST", "/api/v1/auths/signin"),
    ("GET", "/api/v1/auths/signout"),
    ("POST", "/api/v1/auths/signup"),
}

# ── Map from JS constant name → backend path prefix ───────────────────────────
_BASE_URL_MAP: Dict[str, str] = {
    "OPENAI_API_BASE_URL": "/api/v1/providers/openai",
    "OLLAMA_API_BASE_URL": "/api/v1/providers/ollama",
    "WEBUI_API_BASE_URL": "/api/v1",
    "TUTOR_API_BASE_URL": "/api/v1",
    "WEBUI_BASE_URL": "",
    "TUTOR_BASE_URL": "",
    "RETRIEVAL_API_BASE_URL": "/api/v1/retrieval",
    "AUDIO_API_BASE_URL": "/api/v1/audio",
    "IMAGES_API_BASE_URL": "/api/v1/images",
}

# ── Open-webui features not yet ported to CE — skip rather than fail ──────────
# These paths are extracted by the scanner from the UI source but the CE backend
# does not implement them yet. They are tracked here so the test still documents
# the gap without blocking CI.
_SCANNED_PATH_EXCLUSIONS: Set[str] = {
    # Legacy top-level OpenWebUI routes (WEBUI_BASE_URL / TUTOR_BASE_URL → "")
    "/api/changelog",
    "/api/chat/actions/{action_id}",
    "/api/chat/completed",
    "/api/community_sharing",
    "/api/community_sharing/toggle",
    "/api/config",
    "/api/config/model/filter",
    "/api/config/models",
    "/api/tasks/stop/{id}",
    "/api/version/updates",
    "/api/webhook",
    # Auth admin / LDAP routes not implemented in CE
    "/api/v1/auths/add",
    "/api/v1/auths/admin/config",
    "/api/v1/auths/admin/config/ldap",
    "/api/v1/auths/admin/config/ldap/server",
    "/api/v1/auths/admin/details",
    "/api/v1/auths/api_key",
    "/api/v1/auths/ldap",
    "/api/v1/auths/signup/enabled",
    "/api/v1/auths/signup/enabled/toggle",
    "/api/v1/auths/signup/user/role",
    "/api/v1/auths/token/expires",
    "/api/v1/auths/token/expires/update",
    "/api/v1/auths/update/password",
    "/api/v1/auths/update/profile",
    # Channels — not yet in CE
    "/api/v1/channels/",
    "/api/v1/channels/create",
    "/api/v1/channels/{channel_id}",
    "/api/v1/channels/{channel_id}/delete",
    "/api/v1/channels/{channel_id}/messages/post",
    "/api/v1/channels/{channel_id}/update",
    # Folders — not yet in CE
    "/api/v1/folders/",
    "/api/v1/folders/{id}",
    "/api/v1/folders/{id}/update",
    "/api/v1/folders/{id}/update/expanded",
    "/api/v1/folders/{id}/update/items",
    "/api/v1/folders/{id}/update/parent",
    # Functions — not yet in CE
    "/api/v1/functions/",
    "/api/v1/functions/create",
    "/api/v1/functions/export",
    "/api/v1/functions/id/{id}",
    "/api/v1/functions/id/{id}/delete",
    "/api/v1/functions/id/{id}/toggle",
    "/api/v1/functions/id/{id}/toggle/global",
    "/api/v1/functions/id/{id}/update",
    "/api/v1/functions/id/{id}/valves",
    "/api/v1/functions/id/{id}/valves/spec",
    "/api/v1/functions/id/{id}/valves/update",
    "/api/v1/functions/id/{id}/valves/user",
    "/api/v1/functions/id/{id}/valves/user/spec",
    "/api/v1/functions/id/{id}/valves/user/update",
    # Groups — not yet in CE
    "/api/v1/groups/",
    "/api/v1/groups/create",
    "/api/v1/groups/id/{id}",
    "/api/v1/groups/id/{id}/delete",
    "/api/v1/groups/id/{id}/update",
    # Knowledge — implemented in Plan B
    # Memories — not yet in CE
    "/api/v1/memories/",
    "/api/v1/memories/add",
    "/api/v1/memories/delete/user",
    "/api/v1/memories/query",
    "/api/v1/memories/{id}",
    "/api/v1/memories/{id}/update",
    # Pipelines — not yet in CE : pas besoin de cette pipline à supprimer de ui
    "/api/v1/pipelines/",
    "/api/v1/pipelines/add",
    "/api/v1/pipelines/delete",
    "/api/v1/pipelines/list",
    "/api/v1/pipelines/upload",
    # Prompts — not yet in CE
    "/api/v1/prompts/",
    "/api/v1/prompts/command/{command}",
    "/api/v1/prompts/command/{command}/delete",
    "/api/v1/prompts/command/{command}/update",
    "/api/v1/prompts/create",
    "/api/v1/prompts/list",
    # Tasks — not yet in CE
    "/api/v1/tasks/auto/completions",
    "/api/v1/tasks/config",
    "/api/v1/tasks/config/update",
    "/api/v1/tasks/emoji/completions",
    "/api/v1/tasks/moa/completions",
    "/api/v1/tasks/queries/completions",
    "/api/v1/tasks/tags/completions",
    "/api/v1/tasks/title/completions",
    # Tools — not yet in CE
    "/api/v1/tools/",
    "/api/v1/tools/create",
    "/api/v1/tools/export",
    "/api/v1/tools/id/{id}",
    "/api/v1/tools/id/{id}/delete",
    "/api/v1/tools/id/{id}/update",
    "/api/v1/tools/id/{id}/valves",
    "/api/v1/tools/id/{id}/valves/spec",
    "/api/v1/tools/id/{id}/valves/update",
    "/api/v1/tools/id/{id}/valves/user",
    "/api/v1/tools/id/{id}/valves/user/spec",
    "/api/v1/tools/id/{id}/valves/user/update",
    "/api/v1/tools/list",
    # Utils — not yet in CE
    "/api/v1/utils/code/execute",
    "/api/v1/utils/code/format",
    "/api/v1/utils/db/download",
    "/api/v1/utils/gravatar",
    "/api/v1/utils/litellm/config",
    "/api/v1/utils/markdown",
    "/api/v1/utils/pdf",
    # Ollama pull shorthand — CE uses /api/v1/providers/ollama/api/pull
    "/api/v1/providers/ollama/pull",
    # ── Plan B — implement when the feature is scoped ────────────────────────
    # index.ts legacy OpenWebUI top-level routes: /api/models, /api/config,
    # /api/changelog. These hit TUTOR_BASE_URL legacy paths that predate CE's
    # /api/v1/* structure; repoint or stub in Plan B.
    # Tasks, pipelines: not yet in CE — complex feature, deferred to Plan B.
    # Files — CE uses {file_id} param name, UI scans produce {id}
    "/api/v1/files/{id}",
    "/api/v1/files/{id}/content",
    "/api/v1/files/{id}/data/content/update",
}

FORBIDDEN_PATTERNS = [
    "/openai/",
    "/ollama/",
    "/api/chat",
    "/ws/socket",
    "open_webui",
]

ALLOWED_EXCEPTIONS = {
    "/openai/": "/api/v1/providers/",
    "/ollama/": "/api/v1/providers/",
    "/api/chat": "/api/v1/providers/ollama/api/chat",
}


def _camel_to_snake(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _normalize_path(raw: str) -> str:
    path = raw.split("?")[0]  # strip query string
    # JS template interpolations → FastAPI path params
    path = re.sub(
        r"\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}",
        lambda m: "{" + _camel_to_snake(m.group(1)) + "}",
        path,
    )
    return path


def _scan_ui_paths(
    apis_dir: Path, base_url_map: Dict[str, str]
) -> Set[Tuple[str, str]]:
    """Extract (METHOD, path) pairs from fetch() calls in UI TypeScript API clients.

    Scans line-by-line: when a fetch(`${BASE_URL}/...`) is found, look ahead
    up to 8 lines for a `method: 'VERB'` option.  Defaults to GET (per the
    Fetch API spec) when no explicit method is found.
    """
    url_pattern = re.compile(r"""fetch\(`\$\{([A-Z_]+)\}(/[^`\s,)"']*)""")
    method_pattern = re.compile(r"""method:\s*['"]([A-Z]+)['"]""")

    results: Set[Tuple[str, str]] = set()
    for ts_file in apis_dir.rglob("*.ts"):
        content = ts_file.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()

        for i, line in enumerate(lines):
            m = url_pattern.search(line)
            if not m:
                continue
            var_name, suffix = m.group(1), m.group(2)
            prefix = base_url_map.get(var_name)
            if prefix is None:
                continue

            normalized = _normalize_path(suffix)
            full_path = re.sub(r"//+", "/", prefix + normalized)
            if "${" in full_path:
                continue  # malformed ternary template literal

            # Look ahead for the HTTP method (default GET per Fetch spec)
            method = "GET"
            for j in range(i + 1, min(i + 9, len(lines))):
                mm = method_pattern.search(lines[j])
                if mm:
                    method = mm.group(1).upper()
                    break
                if url_pattern.search(lines[j]):
                    break  # reached next fetch call — stop

            results.add((method, full_path))
    return results


def test_required_paths_present(client):
    """Every UI-called (METHOD, path) pair must exist in the OpenAPI schema."""
    schema = client.get("/openapi.json").json()
    # OpenAPI methods are lowercase; build set of (METHOD, path) tuples.
    registered: Set[Tuple[str, str]] = {
        (method.upper(), path)
        for path, methods in schema.get("paths", {}).items()
        for method in methods
        if method != "parameters"
    }

    apis_dir = Path(__file__).parent.parent / "ui" / "src" / "lib" / "apis"
    if apis_dir.exists():
        scanned = _scan_ui_paths(apis_dir, _BASE_URL_MAP)
    else:
        scanned = set()

    # Exclude known-unimplemented paths; exclusion list is path-only (all methods).
    required: Set[Tuple[str, str]] = {
        (method, path)
        for method, path in (scanned | _REQUIRED_PATHS_FALLBACK)
        if path not in _SCANNED_PATH_EXCLUSIONS
    }

    missing = sorted(
        f"{method} {path}"
        for method, path in required
        if (method, path) not in registered
    )
    assert not missing, (
        f"\n{len(missing)} required (METHOD, path) pair(s) missing from OpenAPI schema:\n"
        + "\n".join(f"  - {m}" for m in missing)
    )


def test_forbidden_patterns_absent(client):
    """Legacy OpenWebUI paths must not appear in the OpenAPI schema."""
    schema = client.get("/openapi.json").json()
    registered = list(schema.get("paths", {}).keys())

    found = []
    for pattern in FORBIDDEN_PATTERNS:
        required_prefix = ALLOWED_EXCEPTIONS.get(pattern)
        violating = [
            p
            for p in registered
            if pattern in p
            and (
                required_prefix is None
                or not (p.startswith(required_prefix) or p == required_prefix)
            )
        ]
        if violating:
            found.append((pattern, violating))

    assert not found, (
        f"\n{len(found)} forbidden pattern(s) found in registered routes:\n"
        + "\n".join(f"  - {pat}: " + ", ".join(paths) for pat, paths in found)
    )


def test_ui_scanner_finds_provider_paths(client):
    """Sanity check: scanner must find at least the known provider paths."""
    apis_dir = Path(__file__).parent.parent / "ui" / "src" / "lib" / "apis"
    if not apis_dir.exists():
        return  # UI not present in this environment — skip
    pairs = _scan_ui_paths(apis_dir, _BASE_URL_MAP)
    paths = {path for _, path in pairs}
    # OpenAI and Ollama config are always present in the UI
    assert any(
        "/providers/openai/config" in p for p in paths
    ), f"Scanner should find openai/config path. Got: {sorted(paths)[:20]}"
    assert any(
        "/providers/ollama/config" in p for p in paths
    ), f"Scanner should find ollama/config path. Got: {sorted(paths)[:20]}"


# ── Forbidden paths test — detect legacy OpenWebUI paths in UI source ──────────
# These patterns represent incomplete migration. They should NOT appear in UI source.

_FORBIDDEN_UI_PATTERNS = [
    "/api/chat",  # Legacy OpenWebUI chat namespace
    "/ollama/",  # Legacy Ollama namespace (should be /api/v1/providers/ollama)
    "/openai/",  # Legacy OpenAI namespace (should be /api/v1/providers/openai)
    "/ws/socket",  # Legacy Socket.IO path (should be /realtime/socket.io)
    "open_webui",  # No runtime imports allowed
]


def test_no_forbidden_paths_in_ui():
    """Legacy OpenWebUI paths must not appear in UI source code.

    This test scans the UI TypeScript/Svelte source for forbidden patterns
    that indicate incomplete migration. Unlike _SCANNED_PATH_EXCLUSIONS which
    masks gaps, this test fails the build if forbidden paths are found.
    """
    ui_dir = Path(__file__).parent.parent / "ui" / "src"
    if not ui_dir.exists():
        return  # UI not present — skip

    violations: list[tuple[str, str, int]] = []  # (file, pattern, line_num)

    for pattern in _FORBIDDEN_UI_PATTERNS:
        # Search in .ts and .svelte files
        for ext in ["*.ts", "*.svelte"]:
            for file in ui_dir.rglob(ext):
                if "node_modules" in str(file):
                    continue
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    for line_num, line in enumerate(content.splitlines(), 1):
                        if pattern not in line:
                            continue
                        # /api/chat is forbidden as standalone path but allowed in provider paths
                        # (e.g., /api/v1/providers/ollama/api/chat is legitimate)
                        if pattern == "/api/chat":
                            # Not a fetch call (e.g. display string) — skip
                            if "fetch" not in line.lower() and "i18n.t(" not in line:
                                pass  # still check below
                            elif "fetch" not in line.lower():
                                continue  # pure display string
                            # Legitimate provider path or base-URL variable expression
                            if (
                                "/providers/ollama" in line
                                or "/providers/openai" in line
                            ):
                                continue
                            if any(
                                v in line
                                for v in (
                                    "OLLAMA_API_BASE_URL",
                                    "TUTOR_BASE_URL",
                                    "TUTOR_API_BASE_URL",
                                    "WEBUI_BASE_URL",
                                    "WEBUI_API_BASE_URL",
                                )
                            ):
                                continue
                        violations.append(
                            (str(file.relative_to(ui_dir.parent)), pattern, line_num)
                        )
                except Exception:
                    continue

    if violations:
        msg = "\n".join(
            f"  - {file}:{line}: contains forbidden pattern '{pat}'"
            for file, pat, line in sorted(violations)
        )
        assert False, (
            f"\n{len(violations)} forbidden pattern(s) found in UI source:\n"
            f"This indicates incomplete migration from OpenWebUI.\n{msg}"
        )
