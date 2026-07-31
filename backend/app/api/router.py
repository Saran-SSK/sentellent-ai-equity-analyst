from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.companies import router as companies_router
from app.api.v1.users import router as users_router
from app.api.v1.watchlists import router as watchlists_router
from app.api.v1.portfolios import router as portfolios_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.news import router as news_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(companies_router)
api_router.include_router(users_router)
api_router.include_router(watchlists_router)
api_router.include_router(portfolios_router)
api_router.include_router(chat_router, prefix="/chat")
api_router.include_router(ingestion_router)
api_router.include_router(news_router)
