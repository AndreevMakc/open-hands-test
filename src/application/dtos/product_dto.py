"""
Product Data Transfer Objects

DTOs for product-related operations in the application layer.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator

from ...domain.entities.product import ProductStatus


class ProductCreateDTO(BaseModel):
    """DTO for creating a new product"""
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, max_length=2000, description="Product description")
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    price: Decimal = Field(..., ge=0, description="Product price")
    currency: str = Field(default="RUB", description="Currency code")
    category_id: UUID = Field(..., description="Category ID")
    status: ProductStatus = Field(default=ProductStatus.DRAFT, description="Product status")
    images: List[str] = Field(default_factory=list, description="Product image URLs")
    
    # SEO fields
    seo_title: Optional[str] = Field(None, max_length=255, description="SEO title")
    seo_description: Optional[str] = Field(None, max_length=500, description="SEO description")
    seo_keywords: List[str] = Field(default_factory=list, description="SEO keywords")
    
    @validator('sku')
    def validate_sku(cls, v):
        """Validate SKU format"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('SKU must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()
    
    @validator('images')
    def validate_images(cls, v):
        """Validate image URLs"""
        if len(v) > 10:
            raise ValueError('Maximum 10 images allowed')
        return v


class ProductUpdateDTO(BaseModel):
    """DTO for updating an existing product"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, max_length=2000, description="Product description")
    price: Optional[Decimal] = Field(None, ge=0, description="Product price")
    currency: Optional[str] = Field(None, description="Currency code")
    category_id: Optional[UUID] = Field(None, description="Category ID")
    status: Optional[ProductStatus] = Field(None, description="Product status")
    images: Optional[List[str]] = Field(None, description="Product image URLs")
    
    # SEO fields
    seo_title: Optional[str] = Field(None, max_length=255, description="SEO title")
    seo_description: Optional[str] = Field(None, max_length=500, description="SEO description")
    seo_keywords: Optional[List[str]] = Field(None, description="SEO keywords")
    
    @validator('images')
    def validate_images(cls, v):
        """Validate image URLs"""
        if v is not None and len(v) > 10:
            raise ValueError('Maximum 10 images allowed')
        return v


class ProductResponseDTO(BaseModel):
    """DTO for product response"""
    id: UUID = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    sku: str = Field(..., description="Stock Keeping Unit")
    price: Decimal = Field(..., description="Product price")
    currency: str = Field(..., description="Currency code")
    category_id: UUID = Field(..., description="Category ID")
    status: ProductStatus = Field(..., description="Product status")
    images: List[str] = Field(..., description="Product image URLs")
    
    # SEO fields
    seo_title: Optional[str] = Field(None, description="SEO title")
    seo_description: Optional[str] = Field(None, description="SEO description")
    seo_keywords: List[str] = Field(..., description="SEO keywords")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # Related data
    category_name: Optional[str] = Field(None, description="Category name")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Product attributes")
    
    class Config:
        from_attributes = True


class ProductListDTO(BaseModel):
    """DTO for product list with pagination"""
    products: List[ProductResponseDTO] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")


class ProductFilterDTO(BaseModel):
    """DTO for product filtering"""
    category_id: Optional[UUID] = Field(None, description="Filter by category")
    status: Optional[ProductStatus] = Field(None, description="Filter by status")
    min_price: Optional[Decimal] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Maximum price")
    search: Optional[str] = Field(None, min_length=1, max_length=255, description="Search query")
    sku: Optional[str] = Field(None, description="Filter by SKU")
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    
    # Sorting
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")
    
    @validator('max_price')
    def validate_price_range(cls, v, values):
        """Validate price range"""
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v < values['min_price']:
                raise ValueError('max_price must be greater than or equal to min_price')
        return v


class ProductSearchDTO(BaseModel):
    """DTO for advanced product search"""
    query: Optional[str] = Field(None, description="Search query")
    category_ids: List[UUID] = Field(default_factory=list, description="Category IDs to search in")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Attribute filters")
    price_range: Optional[Dict[str, Decimal]] = Field(None, description="Price range filter")
    status: Optional[List[ProductStatus]] = Field(None, description="Status filters")
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    
    # Sorting
    sort_by: str = Field(default="relevance", description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")
    
    # Search options
    fuzzy: bool = Field(default=False, description="Enable fuzzy search")
    highlight: bool = Field(default=False, description="Highlight search terms")


class ProductAttributeValueDTO(BaseModel):
    """DTO for product attribute value"""
    attribute_id: UUID = Field(..., description="Attribute ID")
    attribute_name: str = Field(..., description="Attribute name")
    value: Any = Field(..., description="Attribute value")
    unit: Optional[str] = Field(None, description="Unit of measurement")


class ProductWithAttributesDTO(ProductResponseDTO):
    """DTO for product with full attribute information"""
    attribute_values: List[ProductAttributeValueDTO] = Field(
        default_factory=list, 
        description="Product attribute values"
    )


class BulkProductOperationDTO(BaseModel):
    """DTO for bulk product operations"""
    product_ids: List[UUID] = Field(..., min_items=1, max_items=100, description="Product IDs")
    operation: str = Field(..., pattern="^(delete|activate|deactivate|archive)$", description="Operation type")
    
    @validator('product_ids')
    def validate_unique_ids(cls, v):
        """Ensure product IDs are unique"""
        if len(v) != len(set(v)):
            raise ValueError('Product IDs must be unique')
        return v


class ProductStatsDTO(BaseModel):
    """DTO for product statistics"""
    total_products: int = Field(..., description="Total number of products")
    active_products: int = Field(..., description="Number of active products")
    draft_products: int = Field(..., description="Number of draft products")
    archived_products: int = Field(..., description="Number of archived products")
    products_by_category: Dict[str, int] = Field(..., description="Products count by category")
    average_price: Optional[Decimal] = Field(None, description="Average product price")
    price_range: Dict[str, Decimal] = Field(..., description="Price range (min/max)")