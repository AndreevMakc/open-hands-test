"""
Product API endpoints

REST API for product management operations.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ....application.use_cases.product_use_cases import ProductUseCases
from ....application.dtos.product_dto import (
    ProductCreateDTO,
    ProductUpdateDTO,
    ProductResponseDTO,
    ProductListDTO,
    ProductFilterDTO,
    ProductSearchDTO,
    BulkProductOperationDTO,
    ProductStatsDTO
)
from ....infrastructure.database.connection import get_db_session
from ....infrastructure.repositories.product_repository import SQLAlchemyProductRepository
from ....infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository


router = APIRouter(prefix="/products", tags=["products"])


async def get_product_use_cases(session=Depends(get_db_session)) -> ProductUseCases:
    """Dependency to get ProductUseCases instance"""
    product_repository = SQLAlchemyProductRepository(session)
    category_repository = SQLAlchemyCategoryRepository(session)
    return ProductUseCases(product_repository, category_repository)


@router.post(
    "/",
    response_model=ProductResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Create a new product with the provided data"
)
async def create_product(
    product_data: ProductCreateDTO,
    use_cases: ProductUseCases = Depends(get_product_use_cases)
) -> ProductResponseDTO:
    """Create a new product"""
    try:
        return await use_cases.create_product(product_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )


@router.get(
    "/",
    response_model=ProductListDTO,
    summary="List products",
    description="Get a paginated list of products with optional filtering"
)
async def list_products(
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    search: Optional[str] = Query(None, min_length=1, description="Search query"),
    sku: Optional[str] = Query(None, description="Filter by SKU"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    use_cases: ProductUseCases = Depends(get_product_use_cases)
) -> ProductListDTO:
    """List products with filtering and pagination"""
    try:
        # Convert status string to enum if provided
        status_enum = None
        if status:
            from ....domain.entities.product import ProductStatus
            try:
                status_enum = ProductStatus(status.upper())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}"
                )
        
        filters = ProductFilterDTO(
            category_id=category_id,
            status=status_enum,
            min_price=min_price,
            max_price=max_price,
            search=search,
            sku=sku,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return await use_cases.list_products(filters)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list products: {str(e)}"
        )


@router.get(
    "/search",
    response_model=ProductListDTO,
    summary="Advanced product search",
    description="Perform advanced search with multiple criteria"
)
async def search_products(
    query: Optional[str] = Query(None, description="Search query"),
    category_ids: List[UUID] = Query([], description="Category IDs to search in"),
    status: List[str] = Query([], description="Status filters"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: str = Query("relevance", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    fuzzy: bool = Query(False, description="Enable fuzzy search"),
    highlight: bool = Query(False, description="Highlight search terms"),
    use_cases: ProductUseCases = Depends(get_product_use_cases)
) -> ProductListDTO:
    """Advanced product search"""
    try:
        # Convert status strings to enums
        status_enums = []
        if status:
            from ....domain.entities.product import ProductStatus
            for s in status:
                try:
                    status_enums.append(ProductStatus(s.upper()))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid status: {s}"
                    )
        
        # Build price range
        price_range = None
        if min_price is not None or max_price is not None:
            price_range = {}
            if min_price is not None:
                price_range['min'] = min_price
            if max_price is not None:
                price_range['max'] = max_price
        
        search_params = ProductSearchDTO(
            query=query,
            category_ids=category_ids,
            status=status_enums if status_enums else None,
            price_range=price_range,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order,
            fuzzy=fuzzy,
            highlight=highlight
        )
        
        return await use_cases.search_products(search_params)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search products: {str(e)}"
        )


@router.get(
    "/{product_id}",
    response_model=ProductResponseDTO,
    summary="Get product by ID",
    description="Retrieve a specific product by its ID"
)
async def get_product(
    product_id: UUID,
    use_cases: ProductUseCases = Depends(get_product_use_cases)
) -> ProductResponseDTO:
    """Get product by ID"""
    try:
        product = await use_cases.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get product: {str(e)}"
        )


@router.get(
    "/sku/{sku}",
    response_model=ProductResponseDTO,
    summary="Get product by SKU",
    description="Retrieve a specific product by its SKU"
)
async def get_product_by_sku(
    sku: str,
    use_cases: ProductUseCases = Depends(get_product_use_cases)
) -> ProductResponseDTO:
    """Get product by SKU"""
    try:
        product = await use_cases.get_product_by_sku(sku)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with SKU {sku} not found"
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get product: {str(e)}"
        )


@router.put(
    "/{product_id}",
    response_model=ProductResponseDTO,
    summary="Update product",
    description="Update an existing product"
)
async def update_product(
    product_id: UUID,
    update_data: ProductUpdateDTO,
    use_cases: ProductUseCases = Depends(get_product_use_cases)
) -> ProductResponseDTO:
    """Update an existing product"""
    try:
        product = await use_cases.update_product(product_id, update_data)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {str(e)}"
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
    description="Delete a product by its ID"
)
async def delete_product(
    product_id: UUID,
    use_cases: ProductUseCases = Depends(get_product_use_cases)
):
    """Delete a product"""
    try:
        success = await use_cases.delete_product(product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete product: {str(e)}"
        )


@router.post(
    "/bulk",
    summary="Bulk operations on products",
    description="Perform bulk operations (delete, activate, deactivate, archive) on multiple products"
)
async def bulk_operation(
    operation_data: BulkProductOperationDTO,
    use_cases: ProductUseCases = Depends(get_product_use_cases)
):
    """Perform bulk operations on products"""
    try:
        result = await use_cases.bulk_operation(operation_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform bulk operation: {str(e)}"
        )


@router.get(
    "/stats/overview",
    response_model=ProductStatsDTO,
    summary="Get product statistics",
    description="Get overview statistics for products"
)
async def get_product_stats(
    use_cases: ProductUseCases = Depends(get_product_use_cases)
) -> ProductStatsDTO:
    """Get product statistics"""
    try:
        return await use_cases.get_product_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get product statistics: {str(e)}"
        )


@router.get(
    "/category/{category_id}",
    response_model=List[ProductResponseDTO],
    summary="Get products by category",
    description="Get all products in a specific category"
)
async def get_products_by_category(
    category_id: UUID,
    include_subcategories: bool = Query(False, description="Include products from subcategories"),
    use_cases: ProductUseCases = Depends(get_product_use_cases)
) -> List[ProductResponseDTO]:
    """Get products by category"""
    try:
        return await use_cases.get_products_by_category(category_id, include_subcategories)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get products by category: {str(e)}"
        )