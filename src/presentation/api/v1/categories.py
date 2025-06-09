"""
Category API endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....application.dtos.category_dto import (
    CategoryCreateDTO, 
    CategoryUpdateDTO, 
    CategoryResponseDTO,
    CategoryListResponseDTO
)
from ....application.use_cases.category_use_cases import CategoryUseCases
from ....infrastructure.database.connection import get_db_session
from ....infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository

router = APIRouter(prefix="/categories", tags=["categories"])


def get_category_use_cases(session: AsyncSession = Depends(get_db_session)) -> CategoryUseCases:
    """Dependency to get category use cases"""
    repository = SQLAlchemyCategoryRepository(session)
    return CategoryUseCases(repository)


@router.post("/", response_model=CategoryResponseDTO, status_code=201)
async def create_category(
    category_data: CategoryCreateDTO,
    use_cases: CategoryUseCases = Depends(get_category_use_cases)
) -> CategoryResponseDTO:
    """Create a new category"""
    try:
        return await use_cases.create_category(category_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=CategoryListResponseDTO)
async def get_categories(
    active_only: bool = Query(True, description="Filter only active categories"),
    search: Optional[str] = Query(None, description="Search query"),
    use_cases: CategoryUseCases = Depends(get_category_use_cases)
) -> CategoryListResponseDTO:
    """Get categories list"""
    if search:
        categories = await use_cases.search_categories(search, active_only)
    elif active_only:
        categories = await use_cases.get_categories_tree()
    else:
        # For now, return all active categories
        # TODO: Implement pagination and filtering
        categories = await use_cases.get_categories_tree()
    
    return CategoryListResponseDTO(
        categories=categories,
        total=len(categories)
    )


@router.get("/roots", response_model=List[CategoryResponseDTO])
async def get_root_categories(
    use_cases: CategoryUseCases = Depends(get_category_use_cases)
) -> List[CategoryResponseDTO]:
    """Get root categories"""
    return await use_cases.get_root_categories()


@router.get("/{category_id}", response_model=CategoryResponseDTO)
async def get_category(
    category_id: UUID,
    use_cases: CategoryUseCases = Depends(get_category_use_cases)
) -> CategoryResponseDTO:
    """Get category by ID"""
    category = await use_cases.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/slug/{slug}", response_model=CategoryResponseDTO)
async def get_category_by_slug(
    slug: str,
    use_cases: CategoryUseCases = Depends(get_category_use_cases)
) -> CategoryResponseDTO:
    """Get category by slug"""
    category = await use_cases.get_category_by_slug(slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/{category_path}/children", response_model=List[CategoryResponseDTO])
async def get_category_children(
    category_path: str,
    use_cases: CategoryUseCases = Depends(get_category_use_cases)
) -> List[CategoryResponseDTO]:
    """Get direct children of a category"""
    return await use_cases.get_category_children(category_path)


@router.put("/{category_id}", response_model=CategoryResponseDTO)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdateDTO,
    use_cases: CategoryUseCases = Depends(get_category_use_cases)
) -> CategoryResponseDTO:
    """Update a category"""
    try:
        return await use_cases.update_category(category_id, category_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    use_cases: CategoryUseCases = Depends(get_category_use_cases)
) -> None:
    """Delete a category"""
    try:
        success = await use_cases.delete_category(category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Category not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))