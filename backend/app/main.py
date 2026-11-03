from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import settings
from app.db import engine
from app.api.yield_curve import india_router, japan_router, router as yield_curve_router, taiwan_router

app = FastAPI(
    title="Fixed Income Analytics API",
    version="1.1.0",
    description="Market data and sovereign yield curve analytics backed by Supabase PostgreSQL."
)

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(yield_curve_router)
app.include_router(india_router)
app.include_router(japan_router)
app.include_router(taiwan_router)

@app.get("/health", tags=["Health"])
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected", "service": "fixed-income-api"}
    except Exception:
        return {"status": "degraded", "database": "unavailable", "service": "fixed-income-api"}
