"""
Cache management API endpoints

REST API for cache monitoring and management operations.
"""

from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from ....application.services.cache_manager import get_cache_manager, CacheManager

router = APIRouter(prefix="/cache", tags=["cache"])


async def get_cache_service() -> CacheManager:
    """Dependency to get CacheManager instance"""
    try:
        return await get_cache_manager()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cache service unavailable: {str(e)}"
        )


@router.get(
    "/health",
    summary="Cache health check",
    description="Check the health status of the cache system"
)
async def cache_health(
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, Any]:
    """Get cache health status"""
    try:
        return await cache_manager.health_check()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get(
    "/stats",
    summary="Cache statistics",
    description="Get comprehensive cache statistics and metrics"
)
async def cache_statistics(
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, Any]:
    """Get cache statistics"""
    try:
        return await cache_manager.get_cache_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache statistics: {str(e)}"
        )


@router.get(
    "/performance",
    summary="Cache performance metrics",
    description="Get cache performance metrics including hit rates"
)
async def cache_performance(
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, Any]:
    """Get cache performance metrics"""
    try:
        return await cache_manager.get_performance_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )


@router.post(
    "/warm",
    summary="Warm cache",
    description="Warm up essential caches for better performance"
)
async def warm_cache(
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, str]:
    """Warm up essential caches"""
    try:
        await cache_manager.warm_essential_caches()
        return {"message": "Cache warming initiated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache warming failed: {str(e)}"
        )


@router.delete(
    "/invalidate/category/{category_id}",
    summary="Invalidate category cache",
    description="Invalidate all caches related to a specific category"
)
async def invalidate_category_cache(
    category_id: UUID,
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, str]:
    """Invalidate category-related caches"""
    try:
        await cache_manager.invalidate_category_related(category_id)
        return {"message": f"Category {category_id} caches invalidated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache invalidation failed: {str(e)}"
        )


@router.delete(
    "/invalidate/product/{product_id}",
    summary="Invalidate product cache",
    description="Invalidate all caches related to a specific product"
)
async def invalidate_product_cache(
    product_id: UUID,
    sku: Optional[str] = None,
    category_id: Optional[UUID] = None,
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, str]:
    """Invalidate product-related caches"""
    try:
        await cache_manager.invalidate_product_related(product_id, sku, category_id)
        return {"message": f"Product {product_id} caches invalidated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache invalidation failed: {str(e)}"
        )


@router.delete(
    "/invalidate/search",
    summary="Invalidate search cache",
    description="Invalidate all search-related caches"
)
async def invalidate_search_cache(
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, str]:
    """Invalidate search-related caches"""
    try:
        await cache_manager.invalidate_all_search()
        return {"message": "Search caches invalidated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search cache invalidation failed: {str(e)}"
        )


@router.delete(
    "/clear",
    summary="Clear all caches",
    description="Clear all caches (use with caution in production)"
)
async def clear_all_caches(
    confirm: bool = False,
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, Any]:
    """Clear all caches"""
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must set confirm=true to clear all caches"
        )
    
    try:
        result = await cache_manager.clear_all_caches()
        return {
            "message": "All caches cleared successfully",
            "results": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear caches: {str(e)}"
        )


@router.get(
    "/memory",
    summary="Cache memory usage",
    description="Get Redis memory usage information"
)
async def cache_memory_usage(
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, Any]:
    """Get cache memory usage"""
    try:
        return await cache_manager.get_cache_memory_usage()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory usage: {str(e)}"
        )


# Category-specific cache endpoints
@router.get(
    "/categories/stats",
    summary="Category cache statistics",
    description="Get detailed statistics for category caches"
)
async def category_cache_stats(
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, Any]:
    """Get category cache statistics"""
    try:
        return await cache_manager.categories.get_cache_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get category cache stats: {str(e)}"
        )


# Product-specific cache endpoints
@router.get(
    "/products/stats",
    summary="Product cache statistics",
    description="Get detailed statistics for product caches"
)
async def product_cache_stats(
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, Any]:
    """Get product cache statistics"""
    try:
        return await cache_manager.products.get_cache_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get product cache stats: {str(e)}"
        )


# Search-specific cache endpoints
@router.get(
    "/search/stats",
    summary="Search cache statistics",
    description="Get detailed statistics for search caches"
)
async def search_cache_stats(
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, Any]:
    """Get search cache statistics"""
    try:
        return await cache_manager.search.get_cache_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search cache stats: {str(e)}"
        )


# Cache configuration endpoints
@router.put(
    "/config/ttl",
    summary="Update cache TTL configuration",
    description="Update TTL (Time To Live) settings for different cache types"
)
async def update_cache_ttl(
    ttl_config: Dict[str, int],
    cache_manager: CacheManager = Depends(get_cache_service)
) -> Dict[str, Any]:
    """Update cache TTL configuration"""
    try:
        success = await cache_manager.update_cache_ttls(ttl_config)
        if success:
            return {
                "message": "Cache TTL configuration updated successfully",
                "config": ttl_config
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update cache TTL configuration"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update TTL config: {str(e)}"
        )