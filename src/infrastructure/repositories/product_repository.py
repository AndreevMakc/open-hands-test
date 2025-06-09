"""
Product repository implementation using SQLAlchemy
"""
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, and_, or_, func, desc, asc, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from ...domain.entities.product import Product, ProductStatus
from ...domain.repositories.product_repository import ProductRepository
from ...domain.value_objects.common import EntityId, Money, SEOData, Timestamps
from ...domain.value_objects.product import SKU, ProductImages
from ..database.models import ProductModel, CategoryModel, ProductAttributeModel


class SQLAlchemyProductRepository(ProductRepository):
    """SQLAlchemy implementation of ProductRepository"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, product: Product) -> Product:
        """Create a new product"""
        model = self._create_model_from_entity(product)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return await self._model_to_entity(model)
    
    async def get_by_id(self, product_id: EntityId) -> Optional[Product]:
        """Get product by ID"""
        stmt = select(ProductModel).options(
            joinedload(ProductModel.category),
            selectinload(ProductModel.product_attributes)
        ).where(ProductModel.id == product_id.value)
        
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return await self._model_to_entity(model) if model else None
    
    async def get_by_sku(self, sku: SKU) -> Optional[Product]:
        """Get product by SKU"""
        stmt = select(ProductModel).options(
            joinedload(ProductModel.category),
            selectinload(ProductModel.product_attributes)
        ).where(ProductModel.sku == sku.value)
        
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return await self._model_to_entity(model) if model else None
    
    async def update(self, product: Product) -> Product:
        """Update an existing product"""
        model = await self._session.get(ProductModel, product.id.value)
        if not model:
            raise ValueError(f"Product with ID {product.id.value} not found")
        
        self._update_model_from_entity(model, product)
        await self._session.flush()
        await self._session.refresh(model)
        return await self._model_to_entity(model)
    
    async def delete(self, product_id: EntityId) -> bool:
        """Delete product by ID"""
        model = await self._session.get(ProductModel, product_id.value)
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
    
    async def list_with_filters(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Product], int]:
        """List products with filters and pagination"""
        conditions = []
        
        # Apply filters
        if 'category_id' in filters:
            conditions.append(ProductModel.category_id == filters['category_id'].value)
        
        if 'status' in filters:
            conditions.append(ProductModel.status == filters['status'])
        
        if 'price_range' in filters:
            price_range = filters['price_range']
            if 'min' in price_range:
                conditions.append(ProductModel.price >= price_range['min'])
            if 'max' in price_range:
                conditions.append(ProductModel.price <= price_range['max'])
        
        if 'search' in filters:
            search_term = f"%{filters['search']}%"
            conditions.append(
                or_(
                    ProductModel.name.ilike(search_term),
                    ProductModel.description.ilike(search_term),
                    ProductModel.sku.ilike(search_term)
                )
            )
        
        if 'sku' in filters:
            conditions.append(ProductModel.sku == filters['sku'])
        
        # Count total
        count_stmt = select(func.count(ProductModel.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Get products
        stmt = select(ProductModel).options(
            joinedload(ProductModel.category),
            selectinload(ProductModel.product_attributes)
        )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Sorting
        sort_column = getattr(ProductModel, sort_by, ProductModel.created_at)
        if sort_order.lower() == "desc":
            stmt = stmt.order_by(desc(sort_column))
        else:
            stmt = stmt.order_by(asc(sort_column))
        
        # Pagination
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        products = [await self._model_to_entity(model) for model in models]
        
        return products, total
    
    async def search(
        self,
        criteria: Dict[str, Any],
        page: int = 1,
        size: int = 20,
        sort_by: str = "relevance",
        sort_order: str = "desc"
    ) -> Tuple[List[Product], int]:
        """Advanced product search"""
        conditions = []
        
        # Text search
        if 'query' in criteria:
            search_term = f"%{criteria['query']}%"
            conditions.append(
                or_(
                    ProductModel.name.ilike(search_term),
                    ProductModel.description.ilike(search_term),
                    ProductModel.sku.ilike(search_term)
                )
            )
        
        # Category filter
        if 'category_ids' in criteria:
            category_ids = [cid.value for cid in criteria['category_ids']]
            conditions.append(ProductModel.category_id.in_(category_ids))
        
        # Price range
        if 'price_range' in criteria:
            price_range = criteria['price_range']
            if 'min' in price_range:
                conditions.append(ProductModel.price >= price_range['min'])
            if 'max' in price_range:
                conditions.append(ProductModel.price <= price_range['max'])
        
        # Status filter
        if 'status' in criteria:
            status_list = criteria['status']
            conditions.append(ProductModel.status.in_(status_list))
        
        # Count total
        count_stmt = select(func.count(ProductModel.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Get products
        stmt = select(ProductModel).options(
            joinedload(ProductModel.category),
            selectinload(ProductModel.product_attributes)
        )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Sorting (simplified for now)
        if sort_by == "relevance":
            stmt = stmt.order_by(ProductModel.name)
        else:
            sort_column = getattr(ProductModel, sort_by, ProductModel.created_at)
            if sort_order.lower() == "desc":
                stmt = stmt.order_by(desc(sort_column))
            else:
                stmt = stmt.order_by(asc(sort_column))
        
        # Pagination
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        products = [await self._model_to_entity(model) for model in models]
        
        return products, total
    
    async def get_by_category_ids(self, category_ids: List[EntityId]) -> List[Product]:
        """Get products by category IDs"""
        category_id_values = [cid.value for cid in category_ids]
        
        stmt = select(ProductModel).options(
            joinedload(ProductModel.category),
            selectinload(ProductModel.product_attributes)
        ).where(ProductModel.category_id.in_(category_id_values))
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [await self._model_to_entity(model) for model in models]
    
    async def bulk_delete(self, product_ids: List[EntityId]) -> int:
        """Bulk delete products"""
        product_id_values = [pid.value for pid in product_ids]
        
        stmt = delete(ProductModel).where(ProductModel.id.in_(product_id_values))
        result = await self._session.execute(stmt)
        await self._session.flush()
        
        return result.rowcount
    
    async def bulk_update_status(self, product_ids: List[EntityId], status: ProductStatus) -> int:
        """Bulk update product status"""
        product_id_values = [pid.value for pid in product_ids]
        
        stmt = update(ProductModel).where(
            ProductModel.id.in_(product_id_values)
        ).values(status=status)
        
        result = await self._session.execute(stmt)
        await self._session.flush()
        
        return result.rowcount
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get product statistics"""
        # Total products
        total_stmt = select(func.count(ProductModel.id))
        total_result = await self._session.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # Products by status
        status_stmt = select(
            ProductModel.status,
            func.count(ProductModel.id)
        ).group_by(ProductModel.status)
        
        status_result = await self._session.execute(status_stmt)
        status_counts = {row[0].value: row[1] for row in status_result.fetchall()}
        
        # Products by category
        category_stmt = select(
            CategoryModel.name,
            func.count(ProductModel.id)
        ).select_from(
            ProductModel.__table__.join(CategoryModel.__table__)
        ).group_by(CategoryModel.name)
        
        category_result = await self._session.execute(category_stmt)
        category_counts = {row[0]: row[1] for row in category_result.fetchall()}
        
        # Price statistics
        price_stmt = select(
            func.min(ProductModel.price),
            func.max(ProductModel.price),
            func.avg(ProductModel.price)
        )
        
        price_result = await self._session.execute(price_stmt)
        price_stats = price_result.fetchone()
        
        return {
            'total': total,
            'active': status_counts.get('active', 0),
            'draft': status_counts.get('draft', 0),
            'archived': status_counts.get('archived', 0),
            'by_category': category_counts,
            'price_range': {
                'min': price_stats[0] if price_stats[0] else 0,
                'max': price_stats[1] if price_stats[1] else 0
            },
            'average_price': price_stats[2] if price_stats[2] else None
        }
    
    def _create_model_from_entity(self, product: Product) -> ProductModel:
        """Create database model from domain entity"""
        return ProductModel(
            id=product.id.value,
            name=product.name,
            description=product.description,
            sku=product.sku.value,
            price=float(product.price.amount),
            currency=product.price.currency,
            category_id=product.category_id.value,
            status=product.status,
            images=product.images.urls if product.images else [],
            seo_title=product.seo_data.title if product.seo_data else None,
            seo_description=product.seo_data.description if product.seo_data else None,
            seo_keywords=product.seo_data.keywords if product.seo_data else [],
            created_at=product.timestamps.created_at,
            updated_at=product.timestamps.updated_at
        )
    
    def _update_model_from_entity(self, model: ProductModel, product: Product) -> None:
        """Update database model from domain entity"""
        model.name = product.name
        model.description = product.description
        model.sku = product.sku.value
        model.price = float(product.price.amount)
        model.currency = product.price.currency
        model.category_id = product.category_id.value
        model.status = product.status
        model.images = product.images.urls if product.images else []
        model.seo_title = product.seo_data.title if product.seo_data else None
        model.seo_description = product.seo_data.description if product.seo_data else None
        model.seo_keywords = product.seo_data.keywords if product.seo_data else []
        model.updated_at = product.timestamps.updated_at
    
    async def _model_to_entity(self, model: ProductModel) -> Product:
        """Convert database model to domain entity"""
        return Product(
            id=EntityId(model.id),
            name=model.name,
            description=model.description,
            sku=SKU(model.sku),
            price=Money(amount=model.price, currency=model.currency or "RUB"),
            category_id=EntityId(model.category_id),
            status=model.status,
            images=ProductImages(urls=model.images or []),
            seo_data=SEOData(
                title=model.seo_title,
                description=model.seo_description,
                keywords=model.seo_keywords or []
            ),
            timestamps=Timestamps(
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        )