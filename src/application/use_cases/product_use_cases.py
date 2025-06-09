"""
Product Use Cases

Business logic for product management operations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

from ...domain.entities.product import Product, ProductStatus
from ...domain.entities.category import Category
from ...domain.value_objects.common import EntityId, Money, SEOData
from ...domain.value_objects.product import SKU, ProductImages
from ...domain.repositories.product_repository import ProductRepository
from ...domain.repositories.category import CategoryRepository
from ..dtos.product_dto import (
    ProductCreateDTO,
    ProductUpdateDTO,
    ProductResponseDTO,
    ProductListDTO,
    ProductFilterDTO,
    ProductSearchDTO,
    ProductWithAttributesDTO,
    BulkProductOperationDTO,
    ProductStatsDTO
)


class ProductUseCases:
    """Use cases for product management"""
    
    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository
    ):
        self._product_repository = product_repository
        self._category_repository = category_repository
    
    async def create_product(self, product_data: ProductCreateDTO) -> ProductResponseDTO:
        """Create a new product"""
        # Verify category exists
        category = await self._category_repository.get_by_id(EntityId(product_data.category_id))
        if not category:
            raise ValueError(f"Category with ID {product_data.category_id} not found")
        
        # Check if SKU is unique
        existing_product = await self._product_repository.get_by_sku(SKU(product_data.sku))
        if existing_product:
            raise ValueError(f"Product with SKU {product_data.sku} already exists")
        
        # Create product entity
        product = Product(
            id=EntityId(),
            name=product_data.name,
            description=product_data.description,
            sku=SKU(product_data.sku),
            price=Money(amount=float(product_data.price), currency=product_data.currency),
            category_id=EntityId(product_data.category_id),
            status=product_data.status,
            images=ProductImages(urls=product_data.images),
            seo_data=SEOData(
                title=product_data.seo_title,
                description=product_data.seo_description,
                keywords=product_data.seo_keywords
            )
        )
        
        # Save product
        saved_product = await self._product_repository.create(product)
        
        # Convert to response DTO
        return await self._product_to_response_dto(saved_product, category)
    
    async def get_product_by_id(self, product_id: UUID) -> Optional[ProductResponseDTO]:
        """Get product by ID"""
        product = await self._product_repository.get_by_id(EntityId(product_id))
        if not product:
            return None
        
        category = await self._category_repository.get_by_id(product.category_id)
        return await self._product_to_response_dto(product, category)
    
    async def get_product_by_sku(self, sku: str) -> Optional[ProductResponseDTO]:
        """Get product by SKU"""
        product = await self._product_repository.get_by_sku(SKU(sku))
        if not product:
            return None
        
        category = await self._category_repository.get_by_id(product.category_id)
        return await self._product_to_response_dto(product, category)
    
    async def update_product(
        self, 
        product_id: UUID, 
        update_data: ProductUpdateDTO
    ) -> Optional[ProductResponseDTO]:
        """Update an existing product"""
        product = await self._product_repository.get_by_id(EntityId(product_id))
        if not product:
            return None
        
        # Verify category exists if being updated
        category = None
        if update_data.category_id:
            category = await self._category_repository.get_by_id(EntityId(update_data.category_id))
            if not category:
                raise ValueError(f"Category with ID {update_data.category_id} not found")
            product.category_id = EntityId(update_data.category_id)
        else:
            category = await self._category_repository.get_by_id(product.category_id)
        
        # Update product fields
        if update_data.name is not None:
            product.name = update_data.name
        
        if update_data.description is not None:
            product.description = update_data.description
        
        if update_data.price is not None:
            currency = update_data.currency or product.price.currency
            product.price = Money(amount=float(update_data.price), currency=currency)
        
        if update_data.status is not None:
            product.status = update_data.status
        
        if update_data.images is not None:
            product.images = ProductImages(urls=update_data.images)
        
        # Update SEO data
        if any([
            update_data.seo_title is not None,
            update_data.seo_description is not None,
            update_data.seo_keywords is not None
        ]):
            product.seo_data = SEOData(
                title=update_data.seo_title or product.seo_data.title,
                description=update_data.seo_description or product.seo_data.description,
                keywords=update_data.seo_keywords or product.seo_data.keywords
            )
        
        # Mark as updated
        product.timestamps = product.timestamps.mark_updated()
        
        # Save updated product
        updated_product = await self._product_repository.update(product)
        return await self._product_to_response_dto(updated_product, category)
    
    async def delete_product(self, product_id: UUID) -> bool:
        """Delete a product"""
        product = await self._product_repository.get_by_id(EntityId(product_id))
        if not product:
            return False
        
        await self._product_repository.delete(EntityId(product_id))
        return True
    
    async def list_products(self, filters: ProductFilterDTO) -> ProductListDTO:
        """List products with filtering and pagination"""
        # Build filter criteria
        filter_criteria = {}
        
        if filters.category_id:
            filter_criteria['category_id'] = EntityId(filters.category_id)
        
        if filters.status:
            filter_criteria['status'] = filters.status
        
        if filters.min_price is not None or filters.max_price is not None:
            price_range = {}
            if filters.min_price is not None:
                price_range['min'] = float(filters.min_price)
            if filters.max_price is not None:
                price_range['max'] = float(filters.max_price)
            filter_criteria['price_range'] = price_range
        
        if filters.search:
            filter_criteria['search'] = filters.search
        
        if filters.sku:
            filter_criteria['sku'] = filters.sku
        
        # Get products with pagination
        products, total = await self._product_repository.list_with_filters(
            filters=filter_criteria,
            page=filters.page,
            size=filters.size,
            sort_by=filters.sort_by,
            sort_order=filters.sort_order
        )
        
        # Convert to response DTOs
        product_dtos = []
        for product in products:
            category = await self._category_repository.get_by_id(product.category_id)
            product_dto = await self._product_to_response_dto(product, category)
            product_dtos.append(product_dto)
        
        # Calculate pagination info
        pages = (total + filters.size - 1) // filters.size
        has_next = filters.page < pages
        has_prev = filters.page > 1
        
        return ProductListDTO(
            products=product_dtos,
            total=total,
            page=filters.page,
            size=filters.size,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
    
    async def search_products(self, search_params: ProductSearchDTO) -> ProductListDTO:
        """Advanced product search"""
        # Build search criteria
        search_criteria = {}
        
        if search_params.query:
            search_criteria['query'] = search_params.query
        
        if search_params.category_ids:
            search_criteria['category_ids'] = [EntityId(cid) for cid in search_params.category_ids]
        
        if search_params.attributes:
            search_criteria['attributes'] = search_params.attributes
        
        if search_params.price_range:
            search_criteria['price_range'] = {
                k: float(v) for k, v in search_params.price_range.items()
            }
        
        if search_params.status:
            search_criteria['status'] = search_params.status
        
        search_criteria['fuzzy'] = search_params.fuzzy
        search_criteria['highlight'] = search_params.highlight
        
        # Perform search
        products, total = await self._product_repository.search(
            criteria=search_criteria,
            page=search_params.page,
            size=search_params.size,
            sort_by=search_params.sort_by,
            sort_order=search_params.sort_order
        )
        
        # Convert to response DTOs
        product_dtos = []
        for product in products:
            category = await self._category_repository.get_by_id(product.category_id)
            product_dto = await self._product_to_response_dto(product, category)
            product_dtos.append(product_dto)
        
        # Calculate pagination info
        pages = (total + search_params.size - 1) // search_params.size
        has_next = search_params.page < pages
        has_prev = search_params.page > 1
        
        return ProductListDTO(
            products=product_dtos,
            total=total,
            page=search_params.page,
            size=search_params.size,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
    
    async def bulk_operation(self, operation_data: BulkProductOperationDTO) -> Dict[str, Any]:
        """Perform bulk operations on products"""
        product_ids = [EntityId(pid) for pid in operation_data.product_ids]
        
        if operation_data.operation == "delete":
            success_count = await self._product_repository.bulk_delete(product_ids)
        elif operation_data.operation == "activate":
            success_count = await self._product_repository.bulk_update_status(
                product_ids, ProductStatus.ACTIVE
            )
        elif operation_data.operation == "deactivate":
            success_count = await self._product_repository.bulk_update_status(
                product_ids, ProductStatus.INACTIVE
            )
        elif operation_data.operation == "archive":
            success_count = await self._product_repository.bulk_update_status(
                product_ids, ProductStatus.ARCHIVED
            )
        else:
            raise ValueError(f"Unknown operation: {operation_data.operation}")
        
        return {
            "operation": operation_data.operation,
            "requested_count": len(operation_data.product_ids),
            "success_count": success_count,
            "failed_count": len(operation_data.product_ids) - success_count
        }
    
    async def get_product_stats(self) -> ProductStatsDTO:
        """Get product statistics"""
        stats = await self._product_repository.get_statistics()
        
        return ProductStatsDTO(
            total_products=stats.get('total', 0),
            active_products=stats.get('active', 0),
            draft_products=stats.get('draft', 0),
            archived_products=stats.get('archived', 0),
            products_by_category=stats.get('by_category', {}),
            average_price=stats.get('average_price'),
            price_range=stats.get('price_range', {'min': 0, 'max': 0})
        )
    
    async def get_products_by_category(
        self, 
        category_id: UUID, 
        include_subcategories: bool = False
    ) -> List[ProductResponseDTO]:
        """Get all products in a category"""
        category_ids = [EntityId(category_id)]
        
        if include_subcategories:
            # Get all subcategory IDs
            subcategories = await self._category_repository.get_children(EntityId(category_id))
            category_ids.extend([cat.id for cat in subcategories])
        
        products = await self._product_repository.get_by_category_ids(category_ids)
        
        # Convert to response DTOs
        product_dtos = []
        for product in products:
            category = await self._category_repository.get_by_id(product.category_id)
            product_dto = await self._product_to_response_dto(product, category)
            product_dtos.append(product_dto)
        
        return product_dtos
    
    async def _product_to_response_dto(
        self, 
        product: Product, 
        category: Optional[Category] = None
    ) -> ProductResponseDTO:
        """Convert product entity to response DTO"""
        return ProductResponseDTO(
            id=product.id.value,
            name=product.name,
            description=product.description,
            sku=product.sku.value,
            price=Decimal(str(product.price.amount)),
            currency=product.price.currency,
            category_id=product.category_id.value,
            status=product.status,
            images=product.images.urls,
            seo_title=product.seo_data.title,
            seo_description=product.seo_data.description,
            seo_keywords=product.seo_data.keywords,
            created_at=product.timestamps.created_at,
            updated_at=product.timestamps.updated_at,
            category_name=category.name if category else None,
            attributes={}  # Will be populated by attribute use cases
        )