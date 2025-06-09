from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.config.settings import settings
from .infrastructure.database.connection import init_database, close_database
from .infrastructure.cache.redis_client import get_redis_client, close_redis_client
from .application.services.cache_manager import get_cache_manager, close_cache_manager
from .presentation.api.v1.categories import router as categories_router
from .presentation.api.v1.products import router as products_router
from .presentation.api.v1.attributes import router as attributes_router
from .presentation.api.v1.cache import router as cache_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_database()
    
    # Initialize Redis and cache manager
    try:
        await get_redis_client()
        await get_cache_manager()
        print("✅ Redis and cache manager initialized")
    except Exception as e:
        print(f"⚠️  Redis initialization failed: {e}")
        print("📝 Application will continue without caching")
    
    yield
    
    # Shutdown
    await close_database()
    await close_cache_manager()
    await close_redis_client()


def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        description=settings.description,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    app.include_router(categories_router, prefix=settings.api_v1_prefix)
    app.include_router(products_router, prefix=settings.api_v1_prefix)
    app.include_router(attributes_router, prefix=settings.api_v1_prefix)
    app.include_router(cache_router, prefix=settings.api_v1_prefix)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        health_status = {
            "status": "healthy", 
            "version": settings.version,
            "database": "connected",
            "cache": "unknown"
        }
        
        # Check cache status
        try:
            cache_manager = await get_cache_manager()
            cache_health = await cache_manager.health_check()
            health_status["cache"] = cache_health.get("status", "unknown")
        except Exception:
            health_status["cache"] = "unavailable"
        
        return health_status
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Product Catalog Service API",
            "version": settings.version,
            "docs": f"{settings.api_v1_prefix}/docs",
            "health": "/health"
        }
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.reload,
        log_level="debug" if settings.debug else "info",
    )