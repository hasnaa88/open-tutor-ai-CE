# 📘 Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-08

### Changed
- 🏗️ **Root-driven architecture**: complete Python application rewrite — zero `open_webui` runtime dependency. Domains now use conventional root packages (`accounts`, `learning`, `ai`, `content`, `governance`, `system`, `gateway`, `data`, `common`, `config`).
- ⚡ **Hermes-style provider layer**: OpenAI and Ollama proxied via `/api/v1/providers/*` with model-list TTL cache and admin-gated configuration.
- 🔌 **Realtime Socket.IO**: remounted at `/realtime/socket.io` with JWT auth — replaces legacy `/ws/socket.io`.
- 🎛️ **TutorAI Control Center**: new admin panel (system prompt, model config, banners) replacing OpenWebUI Settings.
- 🔑 **Auth**: JWT-based authentication replacing OpenWebUI session tokens (`SECRET_KEY` replaces `WEBUI_SECRET_KEY`).
- 🗄️ **Database**: SQLite default via direct SQLAlchemy (no OpenWebUI Base); runtime data isolated to `var/`.
- 📋 **API versioning**: all routes under `/api/v1/*`; forbidden legacy namespaces (`/openai/`, `/ollama/`, `/api/chat/`) removed.

### Added
- ✅ **Contract test**: UI scanner (`test_contract_coverage.py`) dynamically verifies every frontend `fetch()` call has a matching API endpoint.
- 🧩 **Full chat API**: CRUD, archive, pin, share, tags, search, clone, folder (`/api/v1/chats/*`).
- 🤖 **Models overlay API**: custom model config with ownership gating (`/api/v1/models/*`).
- 📡 **Platform API**: version, changelog, banners (`/api/v1/platform/*`).
- 🔄 **Self-regulation domain**: renamed from `evaluations` — HITL feedback with export (`/api/v1/self_regulation/*`).
- 🚦 **CI workflows**: updated for new structure — Python application Black formatting, frontend in `ui/`, release on tag push.

### Removed
- ❌ `open_webui` runtime dependency and all its imports.
- ❌ Legacy namespaces: `/openai/*`, `/ollama/*`, `/api/chat/*`, `/ws/socket.io`.
- ❌ `WEBUI_SECRET_KEY`, `SUPPRESS_WEBUI_BANNER` env vars.

---

## [0.0.1] - 2025-05-12

### Added
- 👩‍🎓 **Student onboarding features**: profile creation, course joining, AI tutor setup, and learning start.
- 🏠 **Learner Space**: personal hub with progress tracking, AI help, and peer interaction.
- 📊 **Smart Dashboard**: deadlines, achievements, and learning overview at a glance.
- 📚 **Course Library**: manage and access all enrolled courses.
- 🧩 **Supports (Personalized Tutorials)**: custom learning paths powered by AI.
- 📝 **Assignment Central**: task management with feedback, deadlines, and points.
- 💬 **Connect & Learn**: messaging system with group and private chat.
- 🤖 **AI Chat Magic**: 24/7 interactive AI tutor with engagement tracking.
- 🌐 **3D Learning World**: immersive learning with avatars and visual lessons.
- ⚙️ **Settings Hub**: profile customization, themes, and privacy controls.
- 🚀 **Smart Tips & Quick Start Guide**: intuitive walkthrough for new learners.

### Fixed
- ✅ Project setup initialized.
- 🧭 Centralized App Launcher in the initial `open_tutorai/main.py` prototype. This historical layout was removed in v1.0.0.
- 📁 Corrected data directory structure — now handled by the Python application, not `openweb-ui`.

### Changed
- 🎨 Updated OpenTutor AI interface and features.
