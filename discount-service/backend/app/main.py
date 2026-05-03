"""
Tolk Discount Service - Main Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import redis.asyncio as redis
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.config.settings import settings
from app.config.database import init_db, close_db
from app.api.routes import auth, users, discounts, stores, categories, collections, health, admin
from app.core.middleware import RateLimitMiddleware
from app.core.cache import CacheManager
from app.core.exceptions import AppException, AppExceptionHandlers

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up application...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize Redis connection
    try:
        app.state.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await app.state.redis.ping()
        logger.info("Redis connection established")
        
        # Initialize cache manager
        app.state.cache = CacheManager(app.state.redis)
        logger.info("Cache manager initialized")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        app.state.redis = None
        app.state.cache = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Close Redis connection
    if hasattr(app.state, 'redis') and app.state.redis:
        await app.state.redis.close()
        logger.info("Redis connection closed")
    
    # Close database connections
    await close_db()
    logger.info("Database connections closed")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Tolk Discount Service API - Platform for managing and sharing discounts",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Add exception handlers
    AppExceptionHandlers.register_handlers(app)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
    )
    
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # Include routers
    app.include_router(health.router, prefix=f"{settings.API_PREFIX}/health", tags=["Health"])
    app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
    app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])
    app.include_router(discounts.router, prefix=f"{settings.API_PREFIX}/discounts", tags=["Discounts"])
    app.include_router(stores.router, prefix=f"{settings.API_PREFIX}/stores", tags=["Stores"])
    app.include_router(categories.router, prefix=f"{settings.API_PREFIX}/categories", tags=["Categories"])
    app.include_router(collections.router, prefix=f"{settings.API_PREFIX}/collections", tags=["Collections"])
    app.include_router(admin.router, prefix=f"{settings.API_PREFIX}/admin", tags=["Admin"])
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint"""
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running"
        }
    
    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
