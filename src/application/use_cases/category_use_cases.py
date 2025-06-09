"""
Category use cases
"""
from typing import List, Optional
from uuid import UUID, uuid4

from ...domain.entities.category import Category
from ...domain.repositories.category import CategoryRepository
from ...domain.value_objects.common import Slug
from ..dtos.category_dto import CategoryCreateDTO, CategoryUpdateDTO, CategoryResponseDTO


class CategoryUseCases:
    """Category business logic use cases"""
    
    def __init__(self, category_repository: CategoryRepository):
        self._category_repository = category_repository
    
    async def create_category(self, dto: CategoryCreateDTO) -> CategoryResponseDTO:
        """Create a new category"""
        # Validate slug uniqueness
        slug = Slug(dto.slug)
        if await self._category_repository.exists_by_slug(slug):
            raise ValueError(f"Category with slug '{dto.slug}' already exists")
        
        # Build path
        path = dto.slug
        if dto.parent_path:
            path = f"{dto.parent_path}.{dto.slug}"
        
        # Create category entity
        category = Category(
            id=uuid4(),
            name=dto.name,
            slug=slug,
            description=dto.description,
            path=path,
            meta_title=dto.meta_title,
            meta_description=dto.meta_description,
            meta_keywords=dto.meta_keywords,
            is_active=dto.is_active,
            sort_order=dto.sort_order or 0
        )
        
        # Save to repository
        saved_category = await self._category_repository.save(category)
        
        return CategoryResponseDTO.from_entity(saved_category)
    
    async def update_category(self, category_id: UUID, dto: CategoryUpdateDTO) -> CategoryResponseDTO:
        """Update an existing category"""
        # Find existing category
        category = await self._category_repository.find_by_id(category_id)
        if not category:
            raise ValueError(f"Category with ID {category_id} not found")
        
        # Validate slug uniqueness if changed
        if dto.slug and dto.slug != str(category.slug):
            new_slug = Slug(dto.slug)
            if await self._category_repository.exists_by_slug(new_slug, exclude_id=category_id):
                raise ValueError(f"Category with slug '{dto.slug}' already exists")
            category.slug = new_slug
        
        # Update fields
        if dto.name is not None:
            category.name = dto.name
        if dto.description is not None:
            category.description = dto.description
        if dto.meta_title is not None:
            category.meta_title = dto.meta_title
        if dto.meta_description is not None:
            category.meta_description = dto.meta_description
        if dto.meta_keywords is not None:
            category.meta_keywords = dto.meta_keywords
        if dto.is_active is not None:
            category.is_active = dto.is_active
        if dto.sort_order is not None:
            category.sort_order = dto.sort_order
        
        # Save updated category
        updated_category = await self._category_repository.save(category)
        
        return CategoryResponseDTO.from_entity(updated_category)
    
    async def get_category(self, category_id: UUID) -> Optional[CategoryResponseDTO]:
        """Get category by ID"""
        category = await self._category_repository.find_by_id(category_id)
        return CategoryResponseDTO.from_entity(category) if category else None
    
    async def get_category_by_slug(self, slug: str) -> Optional[CategoryResponseDTO]:
        """Get category by slug"""
        category = await self._category_repository.find_by_slug(Slug(slug))
        return CategoryResponseDTO.from_entity(category) if category else None
    
    async def get_categories_tree(self) -> List[CategoryResponseDTO]:
        """Get all active categories as a tree structure"""
        categories = await self._category_repository.find_active()
        return [CategoryResponseDTO.from_entity(cat) for cat in categories]
    
    async def get_root_categories(self) -> List[CategoryResponseDTO]:
        """Get root categories"""
        categories = await self._category_repository.find_root_categories()
        return [CategoryResponseDTO.from_entity(cat) for cat in categories]
    
    async def get_category_children(self, category_path: str) -> List[CategoryResponseDTO]:
        """Get direct children of a category"""
        categories = await self._category_repository.find_children(category_path)
        return [CategoryResponseDTO.from_entity(cat) for cat in categories]
    
    async def search_categories(self, query: str, active_only: bool = True) -> List[CategoryResponseDTO]:
        """Search categories"""
        categories = await self._category_repository.search(query, active_only)
        return [CategoryResponseDTO.from_entity(cat) for cat in categories]
    
    async def delete_category(self, category_id: UUID) -> bool:
        """Delete a category"""
        # Check if category exists
        category = await self._category_repository.find_by_id(category_id)
        if not category:
            return False
        
        # Check if category has children
        children = await self._category_repository.find_children(category.path)
        if children:
            raise ValueError("Cannot delete category with children")
        
        # TODO: Check if category has products
        # This would require injecting ProductRepository
        
        return await self._category_repository.delete(category_id)