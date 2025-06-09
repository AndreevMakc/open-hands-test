from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.config.settings import settings
from .infrastructure.database.connection import init_database, close_database
from .presentation.api.v1.categories import router as categories_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_database()
    yield
    # Shutdown
    await close_database()


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
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.version}
    
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