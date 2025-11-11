from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Service health check")
async def healthcheck() -> dict[str, str]:
    """Simple health endpoint for readiness checks."""
    return {"status": "ok"}


