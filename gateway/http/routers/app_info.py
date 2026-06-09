"""Application metadata router exposed as /api/v1/platform/*."""

import os

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from config import settings

router = APIRouter(prefix="/platform", tags=["platform"])

_CHANGELOG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "CHANGELOG.md"
)


@router.get("/version")
async def get_version():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "build_hash": settings.BUILD_HASH,
    }


@router.get("/changelog", response_class=PlainTextResponse)
async def get_changelog():
    try:
        with open(_CHANGELOG_PATH, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


@router.get("/banners")
async def get_banners():
    return []
