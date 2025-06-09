from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.config.settings import settings


def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        description=settings.description,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.version}
    
    # Include routers
    # TODO: Add routers when implemented
    
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