from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.database import init_db
from app.core.middleware import RequestLoggingMiddleware
from app.core.exceptions import register_exception_handlers
from app.config import settings

from app.routers.v1 import api_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.middleware import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    # Ensure static/uploads exists
    os.makedirs("static/uploads", exist_ok=True)
    yield
    # Shutdown

app = FastAPI(
    title="ShoeShop API",
    description="RESTful API cho Website Bán Giày",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
register_exception_handlers(app)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routers
app.include_router(api_router, prefix="/api/v1")

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "Welcome to ShoeShop API"}
