"""
Category repository implementation using SQLAlchemy
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...domain.entities.category import Category
from ...domain.repositories.category import CategoryRepository
from ...domain.value_objects.common import Slug
from ..database.models import CategoryModel


class SQLAlchemyCategoryRepository(CategoryRepository):
    """SQLAlchemy implementation of CategoryRepository"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, category: Category) -> Category:
        """Save category to database"""
        # Check if category exists
        existing = await self._session.get(CategoryModel, category.id)
        
        if existing:
            # Update existing category
            existing.name = category.name
            existing.slug = str(category.slug)
            existing.description = category.description
            existing.path = category.path
            existing.meta_title = category.meta_title
            existing.meta_description = category.meta_description
            existing.meta_keywords = category.meta_keywords
            existing.is_active = category.is_active
            existing.sort_order = category.sort_order
            model = existing
        else:
            # Create new category
            model = CategoryModel(
                id=category.id,
                name=category.name,
                slug=str(category.slug),
                description=category.description,
                path=category.path,
                meta_title=category.meta_title,
                meta_description=category.meta_description,
                meta_keywords=category.meta_keywords,
                is_active=category.is_active,
                sort_order=category.sort_order
            )
            self._session.add(model)
        
        await self._session.flush()
        return self._model_to_entity(model)
    
    async def find_by_id(self, category_id: UUID) -> Optional[Category]:
        """Find category by ID"""
        model = await self._session.get(CategoryModel, category_id)
        return self._model_to_entity(model) if model else None
    
    async def find_by_slug(self, slug: Slug) -> Optional[Category]:
        """Find category by slug"""
        stmt = select(CategoryModel).where(CategoryModel.slug == str(slug))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def find_by_path(self, path: str) -> Optional[Category]:
        """Find category by path"""
        stmt = select(CategoryModel).where(CategoryModel.path == path)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def find_children(self, parent_path: str) -> List[Category]:
        """Find direct children of a category"""
        # Find categories where path starts with parent_path + "."
        # and has exactly one more level
        stmt = select(CategoryModel).where(
            and_(
                CategoryModel.path.like(f"{parent_path}.%"),
                ~CategoryModel.path.like(f"{parent_path}.%.%")
            )
        ).order_by(CategoryModel.sort_order, CategoryModel.name)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def find_descendants(self, parent_path: str) -> List[Category]:
        """Find all descendants of a category"""
        stmt = select(CategoryModel).where(
            CategoryModel.path.like(f"{parent_path}.%")
        ).order_by(CategoryModel.path, CategoryModel.sort_order)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def find_active(self) -> List[Category]:
        """Find all active categories"""
        stmt = select(CategoryModel).where(
            CategoryModel.is_active == True
        ).order_by(CategoryModel.path, CategoryModel.sort_order)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def find_root_categories(self) -> List[Category]:
        """Find root categories (no parent)"""
        stmt = select(CategoryModel).where(
            ~CategoryModel.path.contains(".")
        ).order_by(CategoryModel.sort_order, CategoryModel.name)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def search(self, query: str, active_only: bool = True) -> List[Category]:
        """Search categories by name or description"""
        conditions = [
            or_(
                CategoryModel.name.ilike(f"%{query}%"),
                CategoryModel.description.ilike(f"%{query}%")
            )
        ]
        
        if active_only:
            conditions.append(CategoryModel.is_active == True)
        
        stmt = select(CategoryModel).where(
            and_(*conditions)
        ).order_by(CategoryModel.path, CategoryModel.sort_order)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def delete(self, category_id: UUID) -> bool:
        """Delete category by ID"""
        model = await self._session.get(CategoryModel, category_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
    
    async def exists_by_slug(self, slug: Slug, exclude_id: Optional[UUID] = None) -> bool:
        """Check if category with slug exists"""
        conditions = [CategoryModel.slug == str(slug)]
        
        if exclude_id:
            conditions.append(CategoryModel.id != exclude_id)
        
        stmt = select(CategoryModel.id).where(and_(*conditions))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    def _model_to_entity(self, model: CategoryModel) -> Category:
        """Convert database model to domain entity"""
        return Category(
            id=model.id,
            name=model.name,
            slug=Slug(model.slug),
            description=model.description,
            path=model.path,
            meta_title=model.meta_title,
            meta_description=model.meta_description,
            meta_keywords=model.meta_keywords,
            is_active=model.is_active,
            sort_order=model.sort_order,
            created_at=model.created_at,
            updated_at=model.updated_at
        )