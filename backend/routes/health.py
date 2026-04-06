import os

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "version": "1.0.0",
        "model": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "mock"),
    }
