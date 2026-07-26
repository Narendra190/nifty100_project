import sqlite3
import time
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import (
    companies,
    screener,
    sectors,
    peers,
    valuation,
    portfolio,
    documents,
    health,
)

# ============================================================
# App Initialization
# ============================================================

app = FastAPI(
    title="Nifty100 Financial Analytics API",
    version="1.0.0",
    description="Sprint 6 - FastAPI Backend"
)

@app.get("/")
def root():
    return {
        "message": "Welcome to Nifty100 Financial Analytics API",
        "docs": "/docs"
    }

APP_START_TIME = time.time()

# ============================================================
# SQLite Connection
# ============================================================

DATABASE_PATH = "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# Logging Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ============================================================
# CORS Middleware
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Internal use only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Request Logging Middleware
# ============================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):

    start = time.time()

    response = await call_next(request)

    elapsed = time.time() - start

    logger.info(
        f"{request.method} "
        f"{request.url.path} "
        f"{elapsed:.3f}s"
    )

    return response

# ============================================================
# Include Routers
# ============================================================

app.include_router(
    health.router,
    prefix="/api/v1/health",
    tags=["Health"]
)

app.include_router(
    companies.router,
    prefix="/api/v1/companies",
    tags=["Companies"]
)

app.include_router(
    screener.router,
    prefix="/api/v1/screener",
    tags=["Screener"]
)

app.include_router(
    sectors.router,
    prefix="/api/v1/sectors",
    tags=["Sectors"]
)

app.include_router(
    peers.router,
    prefix="/api/v1/peers",
    tags=["Peers"]
)

app.include_router(
    valuation.router,
    prefix="/api/v1/valuation",
    tags=["Valuation"]
)

app.include_router(
    portfolio.router,
    prefix="/api/v1/portfolio",
    tags=["Portfolio"]
)

app.include_router(
    documents.router,
    prefix="/api/v1/documents",
    tags=["Documents"]
)