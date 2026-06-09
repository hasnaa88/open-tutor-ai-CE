# Open TutorAI CE — Claude Code Instructions

## Project Overview

Open TutorAI CE is a standalone educational AI platform. The Python application is
a FastAPI root-driven application following the Hermes pattern. The frontend is
SvelteKit in `ui/`.

**Rule #1 — never import from `open_webui` at runtime.** Use the open-webui repo
(`/Volumes/Work/Develop/Projects/Team_RD/opentutorai/open-webui`) as a read-only
reference only.

---

## Running Commands

```bash
# Python application tests (fast — SQLite in-memory)
~/.pyenv/versions/tutorai-env/bin/pytest -q

# Run a specific test file
~/.pyenv/versions/tutorai-env/bin/pytest tests/test_chats.py -v

# Python application format check
~/.pyenv/versions/tutorai-env/bin/black . --check --exclude ".venv/|/venv/|ui/"

# Apply Black formatting
~/.pyenv/versions/tutorai-env/bin/black . --exclude ".venv/|/venv/|ui/"

# Frontend dev server
cd ui && npm run dev

# Frontend tests
cd ui && npm run test:frontend
```

---

## Architecture — Python Application

```
main.py                    ← uvicorn entry point
accounts/                  ← auth, users, roles, permissions
learning/                  ← learners, teachers, classrooms, courses, sessions, supports
ai/                        ← llm, providers, retrieval/RAG, media, memory, tools
content/                   ← files and learning resources not tied to RAG
governance/                ← HITL evaluation and policy domains
system/                    ← app-level configs and app info/bootstrap services
gateway/
  http/
    app.py                 ← FastAPI app factory, lifespan, CORS, router registration
    dependencies.py        ← Depends() factories: auth guard, service injection
    routers/<domain>.py    ← One router per domain, thin HTTP layer only
  realtime/
    socket.py              ← Socket.IO ASGI, JWT auth, SESSION_POOL
data/
  database.py              ← SQLAlchemy engine + get_db() session factory
  models/                  ← ORM models (one file per entity)
  repositories/base.py     ← Generic CRUD base
```

OpenWebUI and Hermes are read-only references for UI contract and implementation
techniques. They must not be imported at runtime and their package names should not
drive OpenTutorAI's internal domain names.

### Domain pattern (mandatory for every domain)

```python
# 1. repository.py — only data access
class ChatRepository(BaseRepository[Chat]):
    def get_by_share_id(self, share_id: str) -> Optional[Chat]: ...

# 2. service.py — only business logic
class ChatsService:
    def __init__(self, session: Session):
        self.repo = ChatRepository(session, Chat)

    def get(self, chat_id: str, user_id: str) -> Chat:
        chat = self.repo.get_by_id(chat_id)
        if not chat:
            raise NotFoundError("Chat", chat_id)
        if chat.user_id != user_id:
            raise AuthorizationError("Not authorized")
        return chat

# 3. router — only HTTP concerns, delegates to service
@router.get("/{id}")
def get_chat(id: str, user=Depends(require_user), svc=Depends(get_chats_service)):
    return svc.get(id, user.id)
```

### Adding a new domain

1. Choose the correct boundary first: `accounts`, `learning`, `ai`, `content`, `governance`, or `system`
2. Create `<boundary>/<domain>/repository.py`, `<boundary>/<domain>/service.py`, `<boundary>/<domain>/__init__.py`
3. Add ORM model in `data/models/<domain>.py`, register in `data/models/__init__.py`
4. Create `gateway/http/routers/<public_namespace>.py`
5. Register router in `gateway/http/app.py`
6. Add tests in `tests/test_<domain>.py`
7. Remove the route from `_SCANNED_PATH_EXCLUSIONS` in `tests/test_contract_coverage.py`

---

## Architecture — Frontend

```
ui/src/lib/apis/<domain>/index.ts   ← API client (fetch calls)
ui/src/lib/components/              ← Reusable Svelte components
ui/src/routes/                      ← File-based routing
ui/src/lib/i18n/locales/            ← Translations (AR / FR / EN)
```

**Every `fetch()` call in `ui/src/lib/apis/` must have a matching API endpoint.**
The contract test (`tests/test_contract_coverage.py`) enforces this in CI.

---

## Key Constraints

| Rule | Detail |
|------|--------|
| No `open_webui` imports | Never `from open_webui import ...` at runtime |
| Black 24.8.0 | Formatter pinned — run before committing |
| No ORM in routers | Routers call services only |
| No business logic in repositories | Pure data access |
| Contract test | Every UI `fetch()` needs an API route |
| Auth | JWT via `decode_jwt_token` in `gateway/http/dependencies.py` |
| DB | Sync SQLAlchemy + `get_db()` — no async ORM |
| Secrets | Never commit `.env`, never hardcode keys |

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEBUG` | `true` | Bypasses SECRET_KEY strength check in dev |
| `SECRET_KEY` | *(dev placeholder)* | JWT signing key |
| `DATABASE_URL` | `sqlite:///./var/tutorai.db` | SQLAlchemy URL |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `OPENAI_API_BASE_URL` | *(empty)* | OpenAI-compatible API |
| `CORS_ALLOW_ORIGIN` | `http://localhost:3000,...` | Allowed CORS origins |

---

## CI Workflows

| File | Trigger | Jobs |
|------|---------|------|
| `ci-backend.yaml` | push/PR → main, dev | Python app `lint` (Black) → `test` (pytest) |
| `ci-frontend.yaml` | push/PR → main, dev | `build` (format+i18n+build) + `test` (vitest) |
| `build-release.yml` | push tag `v*` | GitHub release from CHANGELOG |

**CI uses `requirements-ci.txt`** (minimal deps, fast install) — not the full `requirements.txt`.

---

## DevOps

```
devops/
  docker/               ← Dockerfiles + Docker Compose overlays
  scripts/
    dev.sh              ← Local Python API hot-reload (loads .env, uvicorn --reload)
    run.sh              ← Build + run single Docker container
    run-compose.sh      ← Full Compose stack with GPU/API flags
    run-ollama-docker.sh← Start Ollama in Docker
```

```bash
# Local dev (Python API)
./devops/scripts/dev.sh

# Docker Compose (full stack)
docker compose -f devops/docker/docker-compose.yaml up --build

# GPU
docker compose -f devops/docker/docker-compose.yaml \
               -f devops/docker/docker-compose.gpu.yaml up --build
```

---

## Reference Repos (read-only)

- **open-webui**: `/Volumes/Work/Develop/Projects/Team_RD/opentutorai/open-webui`
- **hermes-agent**: `/Volumes/Work/Develop/Projects/Team_RD/opentutorai/hermes-agent`

Use `grep` / `Read` on these to understand patterns. Never import from them.
