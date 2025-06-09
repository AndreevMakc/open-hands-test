"""
Category Data Transfer Objects
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ...domain.entities.category import Category


class CategoryCreateDTO(BaseModel):
    """DTO for creating a category"""
    name: str = Field(..., min_length=1, max_length=255, description="Category name")
    slug: str = Field(..., min_length=1, max_length=255, description="Category slug")
    description: Optional[str] = Field(None, description="Category description")
    parent_path: Optional[str] = Field(None, description="Parent category path")
    meta_title: Optional[str] = Field(None, max_length=255, description="SEO meta title")
    meta_description: Optional[str] = Field(None, description="SEO meta description")
    meta_keywords: Optional[str] = Field(None, description="SEO meta keywords")
    is_active: bool = Field(True, description="Whether category is active")
    sort_order: Optional[int] = Field(0, description="Sort order")


class CategoryUpdateDTO(BaseModel):
    """DTO for updating a category"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Category name")
    slug: Optional[str] = Field(None, min_length=1, max_length=255, description="Category slug")
    description: Optional[str] = Field(None, description="Category description")
    meta_title: Optional[str] = Field(None, max_length=255, description="SEO meta title")
    meta_description: Optional[str] = Field(None, description="SEO meta description")
    meta_keywords: Optional[str] = Field(None, description="SEO meta keywords")
    is_active: Optional[bool] = Field(None, description="Whether category is active")
    sort_order: Optional[int] = Field(None, description="Sort order")


class CategoryResponseDTO(BaseModel):
    """DTO for category response"""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    path: str
    meta_title: Optional[str]
    meta_description: Optional[str]
    meta_keywords: Optional[str]
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_entity(cls, category: Category) -> "CategoryResponseDTO":
        """Create DTO from domain entity"""
        return cls(
            id=category.id,
            name=category.name,
            slug=str(category.slug),
            description=category.description,
            path=category.path,
            meta_title=category.meta_title,
            meta_description=category.meta_description,
            meta_keywords=category.meta_keywords,
            is_active=category.is_active,
            sort_order=category.sort_order,
            created_at=category.created_at,
            updated_at=category.updated_at
        )


class CategoryListResponseDTO(BaseModel):
    """DTO for category list response"""
    categories: list[CategoryResponseDTO]
    total: int