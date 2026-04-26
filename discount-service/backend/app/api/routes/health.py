"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
import redis.asyncio as redis

from app.config.database import get_db
from app.models.schemas import APIResponse

router = APIRouter()


@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "discount-service"
    }


@router.get("/db")
async def database_health(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": f"error: {str(e)}"
        }


@router.get("/redis")
async def redis_health(request):
    """Redis health check"""
    try:
        redis_client = request.app.state.redis
        if redis_client:
            await redis_client.ping()
            return {
                "status": "healthy",
                "redis": "connected"
            }
        else:
            return {
                "status": "degraded",
                "redis": "not configured"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "redis": f"error: {str(e)}"
        }


@router.get("/full")
async def full_health_check(db: Session = Depends(get_db), request=None):
    """Full system health check"""
    health_status = {
        "status": "healthy",
        "checks": {}
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        redis_client = request.app.state.redis if request else None
        if redis_client:
            await redis_client.ping()
            health_status["checks"]["redis"] = "healthy"
        else:
            health_status["checks"]["redis"] = "not configured"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status
