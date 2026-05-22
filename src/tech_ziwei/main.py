from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tech_ziwei.config import settings
from tech_ziwei.middleware import RateLimitMiddleware
from tech_ziwei.routers import auth_router, users_router, charts_router, payments_router, preview_router

app = FastAPI(
    title="Tech Zi Wei",
    description="Psychological Zi Wei Dou Shu astrology platform",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(charts_router)
app.include_router(payments_router)
app.include_router(preview_router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
