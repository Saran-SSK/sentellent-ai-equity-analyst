from fastapi import APIRouter

router = APIRouter(prefix="/health")


@router.get("")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "Sentellent AI Equity Analyst",
    }
