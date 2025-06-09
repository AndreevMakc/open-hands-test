"""
Product repository implementation using SQLAlchemy
"""
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from ...domain.entities.product import Product
from ...domain.repositories.product_repository import ProductRepository
from ...domain.value_objects.common import Slug
from ...domain.value_objects.product import SKU, ProductStatus
from ..database.models import ProductModel, CategoryModel, ProductAttributeModel


class SQLAlchemyProductRepository(ProductRepository):
    """SQLAlchemy implementation of ProductRepository"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, product: Product) -> Product:
        """Save product to database"""
        # Check if product exists
        existing = await self._session.get(ProductModel, product.id)
        
        if existing:
            # Update existing product
            self._update_model_from_entity(existing, product)
            model = existing
        else:
            # Create new product
            model = self._create_model_from_entity(product)
            self._session.add(model)
        
        await self._session.flush()
        return await self._model_to_entity(model)
    
    async def find_by_id(self, product_id: UUID) -> Optional[Product]:
        """Find product by ID"""
        stmt = select(ProductModel).options(
            joinedload(ProductModel.category),
            selectinload(ProductModel.product_attributes)
        ).where(ProductModel.id == product_id)
        
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return await self._model_to_entity(model) if model else None
    
    async def find_by_slug(self, slug: Slug) -> Optional[Product]:
        """Find product by slug"""
        stmt = select(ProductModel).options(
            joinedload(ProductModel.category),
            selectinload(ProductModel.product_attributes)
        ).where(ProductModel.slug == str(slug))
        
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return await self._model_to_entity(model) if model else None
    
    async def find_by_sku(self, sku: SKU) -> Optional[Product]:
        """Find product by SKU"""
        stmt = select(ProductModel).options(
            joinedload(ProductModel.category),
            selectinload(ProductModel.product_attributes)
        ).where(ProductModel.sku == str(sku))
        
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return await self._model_to_entity(model) if model else None
    
    async def find_by_category(
        self, 
        category_id: UUID, 
        include_descendants: bool = False,
        status: Optional[ProductStatus] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Product]:
        """Find products by category"""
        conditions = []
        
        if include_descendants:
            # Get category path first
            category_stmt = select(CategoryModel.path).where(CategoryModel.id == category_id)
            category_result = await self._session.execute(category_stmt)
            category_path = category_result.scalar_one_or_none()
            
            if category_path:
                # Find all categories that are descendants
                descendant_stmt = select(CategoryModel.id).where(
                    or_(
                        CategoryModel.id == category_id,
                        CategoryModel.path.like(f"{category_path}.%")
                    )
                )
                descendant_result = await self._session.execute(descendant_stmt)
                descendant_ids = [row[0] for row in descendant_result.fetchall()]
                conditions.append(ProductModel.category_id.in_(descendant_ids))
            else:
                conditions.append(ProductModel.category_id == category_id)
        else:
            conditions.append(ProductModel.category_id == category_id)
        
        if status:
            conditions.append(ProductModel.status == status)
        
        stmt = select(ProductModel).options(
            joinedload(ProductModel.category),
            selectinload(ProductModel.product_attributes)
        ).where(and_(*conditions)).order_by(ProductModel.sort_order, ProductModel.name)
        
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [await self._model_to_entity(model) for model in models]
    
    async def search(
        self,
        query: str,
        category_id: Optional[UUID] = None,
        status: Optional[ProductStatus] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        attributes: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> List[Product]:
        """Search products with filters"""
        conditions = []
        
        # Text search
        if query:
            conditions.append(
                or_(
                    ProductModel.name.ilike(f"%{query}%"),
                    ProductModel.description.ilike(f"%{query}%"),
                    ProductModel.short_description.ilike(f"%{query}%"),
                    ProductModel.sku.ilike(f"%{query}%")
                )
            )
        
        # Category filter
        if category_id:
            conditions.append(ProductModel.category_id == category_id)
        
        # Status filter
        if status:
            conditions.append(ProductModel.status == status)
        
        # Price range filter
        if min_price is not None:
            conditions.append(ProductModel.price >= min_price)
        if max_price is not None:
            conditions.append(ProductModel.price <= max_price)
        
        stmt = select(ProductModel).options(
            joinedload(ProductModel.category),
            selectinload(ProductModel.product_attributes)
        )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Sorting
        sort_column = getattr(ProductModel, sort_by, ProductModel.name)
        if sort_order.lower() == "desc":
            stmt = stmt.order_by(desc(sort_column))
        else:
            stmt = stmt.order_by(asc(sort_column))
        
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [await self._model_to_entity(model) for model in models]
    
    async def find_featured(self, limit: Optional[int] = None) -> List[Product]:
        """Find featured products"""
        stmt = select(ProductModel).options(
            joinedload(ProductModel.category),
            selectinload(ProductModel.product_attributes)
        ).where(
            and_(
                ProductModel.is_featured == True,
                ProductModel.status == ProductStatus.ACTIVE
            )
        ).order_by(ProductModel.sort_order, ProductModel.name)
        
        if limit:
            stmt = stmt.limit(limit)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [await self._model_to_entity(model) for model in models]
    
    async def count_by_category(self, category_id: UUID) -> int:
        """Count products in category"""
        stmt = select(func.count(ProductModel.id)).where(
            ProductModel.category_id == category_id
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def delete(self, product_id: UUID) -> bool:
        """Delete product by ID"""
        model = await self._session.get(ProductModel, product_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
    
    async def exists_by_slug(self, slug: Slug, exclude_id: Optional[UUID] = None) -> bool:
        """Check if product with slug exists"""
        conditions = [ProductModel.slug == str(slug)]
        
        if exclude_id:
            conditions.append(ProductModel.id != exclude_id)
        
        stmt = select(ProductModel.id).where(and_(*conditions))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def exists_by_sku(self, sku: SKU, exclude_id: Optional[UUID] = None) -> bool:
        """Check if product with SKU exists"""
        conditions = [ProductModel.sku == str(sku)]
        
        if exclude_id:
            conditions.append(ProductModel.id != exclude_id)
        
        stmt = select(ProductModel.id).where(and_(*conditions))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    def _create_model_from_entity(self, product: Product) -> ProductModel:
        """Create database model from domain entity"""
        return ProductModel(
            id=product.id,
            name=product.name,
            slug=str(product.slug),
            description=product.description,
            short_description=product.short_description,
            sku=str(product.sku),
            price=product.price,
            compare_price=product.compare_price,
            cost_price=product.cost_price,
            track_inventory=product.track_inventory,
            inventory_quantity=product.inventory_quantity,
            allow_backorder=product.allow_backorder,
            weight=product.weight,
            length=product.length,
            width=product.width,
            height=product.height,
            images=product.images.gallery if product.images else None,
            meta_title=product.meta_title,
            meta_description=product.meta_description,
            meta_keywords=product.meta_keywords,
            status=product.status,
            is_featured=product.is_featured,
            sort_order=product.sort_order,
            category_id=product.category_id
        )
    
    def _update_model_from_entity(self, model: ProductModel, product: Product) -> None:
        """Update database model from domain entity"""
        model.name = product.name
        model.slug = str(product.slug)
        model.description = product.description
        model.short_description = product.short_description
        model.sku = str(product.sku)
        model.price = product.price
        model.compare_price = product.compare_price
        model.cost_price = product.cost_price
        model.track_inventory = product.track_inventory
        model.inventory_quantity = product.inventory_quantity
        model.allow_backorder = product.allow_backorder
        model.weight = product.weight
        model.length = product.length
        model.width = product.width
        model.height = product.height
        model.images = product.images.gallery if product.images else None
        model.meta_title = product.meta_title
        model.meta_description = product.meta_description
        model.meta_keywords = product.meta_keywords
        model.status = product.status
        model.is_featured = product.is_featured
        model.sort_order = product.sort_order
        model.category_id = product.category_id
    
    async def _model_to_entity(self, model: ProductModel) -> Product:
        """Convert database model to domain entity"""
        # Convert images
        images = None
        if model.images:
            from ...domain.value_objects.product import ProductImages
            images = ProductImages(gallery=model.images)
        
        return Product(
            id=model.id,
            name=model.name,
            slug=Slug(model.slug),
            description=model.description,
            short_description=model.short_description,
            sku=SKU(model.sku),
            price=model.price,
            compare_price=model.compare_price,
            cost_price=model.cost_price,
            track_inventory=model.track_inventory,
            inventory_quantity=model.inventory_quantity,
            allow_backorder=model.allow_backorder,
            weight=model.weight,
            length=model.length,
            width=model.width,
            height=model.height,
            images=images,
            meta_title=model.meta_title,
            meta_description=model.meta_description,
            meta_keywords=model.meta_keywords,
            status=model.status,
            is_featured=model.is_featured,
            sort_order=model.sort_order,
            category_id=model.category_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )