"""Health check router."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Check application health."""
    return {"status": "healthy"}


@router.post("")
async def health_check_post():
    """Health check POST endpoint for compatibility."""
    return {"status": "healthy"}
