"""
Attribute Data Transfer Objects

DTOs for attribute-related operations in the application layer.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator

from ...domain.entities.attribute import AttributeType


class AttributeCreateDTO(BaseModel):
    """DTO for creating a new attribute"""
    name: str = Field(..., min_length=1, max_length=255, description="Attribute name")
    description: Optional[str] = Field(None, max_length=1000, description="Attribute description")
    type: AttributeType = Field(..., description="Attribute type")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    is_required: bool = Field(default=False, description="Is attribute required")
    is_filterable: bool = Field(default=True, description="Can be used for filtering")
    is_searchable: bool = Field(default=False, description="Can be used for search")
    
    # Validation rules
    min_value: Optional[float] = Field(None, description="Minimum value (for numeric types)")
    max_value: Optional[float] = Field(None, description="Maximum value (for numeric types)")
    min_length: Optional[int] = Field(None, ge=0, description="Minimum length (for string types)")
    max_length: Optional[int] = Field(None, ge=1, description="Maximum length (for string types)")
    allowed_values: List[str] = Field(default_factory=list, description="Allowed values (for enum types)")
    regex_pattern: Optional[str] = Field(None, description="Regex pattern for validation")
    
    # Display options
    display_order: int = Field(default=0, description="Display order")
    group_name: Optional[str] = Field(None, max_length=100, description="Attribute group name")
    
    @validator('max_value')
    def validate_value_range(cls, v, values):
        """Validate value range"""
        if v is not None and 'min_value' in values and values['min_value'] is not None:
            if v <= values['min_value']:
                raise ValueError('max_value must be greater than min_value')
        return v
    
    @validator('max_length')
    def validate_length_range(cls, v, values):
        """Validate length range"""
        if v is not None and 'min_length' in values and values['min_length'] is not None:
            if v <= values['min_length']:
                raise ValueError('max_length must be greater than min_length')
        return v
    
    @validator('allowed_values')
    def validate_allowed_values(cls, v, values):
        """Validate allowed values for enum types"""
        if 'type' in values and values['type'] == AttributeType.ENUM:
            if not v:
                raise ValueError('allowed_values is required for enum type')
            if len(v) != len(set(v)):
                raise ValueError('allowed_values must be unique')
        return v


class AttributeUpdateDTO(BaseModel):
    """DTO for updating an existing attribute"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Attribute name")
    description: Optional[str] = Field(None, max_length=1000, description="Attribute description")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    is_required: Optional[bool] = Field(None, description="Is attribute required")
    is_filterable: Optional[bool] = Field(None, description="Can be used for filtering")
    is_searchable: Optional[bool] = Field(None, description="Can be used for search")
    
    # Validation rules
    min_value: Optional[float] = Field(None, description="Minimum value (for numeric types)")
    max_value: Optional[float] = Field(None, description="Maximum value (for numeric types)")
    min_length: Optional[int] = Field(None, ge=0, description="Minimum length (for string types)")
    max_length: Optional[int] = Field(None, ge=1, description="Maximum length (for string types)")
    allowed_values: Optional[List[str]] = Field(None, description="Allowed values (for enum types)")
    regex_pattern: Optional[str] = Field(None, description="Regex pattern for validation")
    
    # Display options
    display_order: Optional[int] = Field(None, description="Display order")
    group_name: Optional[str] = Field(None, max_length=100, description="Attribute group name")


class AttributeResponseDTO(BaseModel):
    """DTO for attribute response"""
    id: UUID = Field(..., description="Attribute ID")
    name: str = Field(..., description="Attribute name")
    description: Optional[str] = Field(None, description="Attribute description")
    type: AttributeType = Field(..., description="Attribute type")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    is_required: bool = Field(..., description="Is attribute required")
    is_filterable: bool = Field(..., description="Can be used for filtering")
    is_searchable: bool = Field(..., description="Can be used for search")
    
    # Validation rules
    min_value: Optional[float] = Field(None, description="Minimum value")
    max_value: Optional[float] = Field(None, description="Maximum value")
    min_length: Optional[int] = Field(None, description="Minimum length")
    max_length: Optional[int] = Field(None, description="Maximum length")
    allowed_values: List[str] = Field(..., description="Allowed values")
    regex_pattern: Optional[str] = Field(None, description="Regex pattern")
    
    # Display options
    display_order: int = Field(..., description="Display order")
    group_name: Optional[str] = Field(None, description="Attribute group name")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # Usage statistics
    categories_count: int = Field(default=0, description="Number of categories using this attribute")
    products_count: int = Field(default=0, description="Number of products with this attribute")
    
    class Config:
        from_attributes = True


class AttributeListDTO(BaseModel):
    """DTO for attribute list with pagination"""
    attributes: List[AttributeResponseDTO] = Field(..., description="List of attributes")
    total: int = Field(..., description="Total number of attributes")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")


class AttributeFilterDTO(BaseModel):
    """DTO for attribute filtering"""
    type: Optional[AttributeType] = Field(None, description="Filter by type")
    is_required: Optional[bool] = Field(None, description="Filter by required status")
    is_filterable: Optional[bool] = Field(None, description="Filter by filterable status")
    is_searchable: Optional[bool] = Field(None, description="Filter by searchable status")
    group_name: Optional[str] = Field(None, description="Filter by group name")
    search: Optional[str] = Field(None, min_length=1, max_length=255, description="Search query")
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    
    # Sorting
    sort_by: str = Field(default="display_order", description="Sort field")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Sort order")


class CategoryAttributeDTO(BaseModel):
    """DTO for category-attribute relationship"""
    category_id: UUID = Field(..., description="Category ID")
    attribute_id: UUID = Field(..., description="Attribute ID")
    is_inherited: bool = Field(default=False, description="Is inherited from parent category")
    display_order: Optional[int] = Field(None, description="Display order in category")


class CategoryAttributeCreateDTO(BaseModel):
    """DTO for creating category-attribute relationship"""
    attribute_ids: List[UUID] = Field(..., min_items=1, description="Attribute IDs to assign")
    inherit_to_children: bool = Field(default=False, description="Inherit to child categories")
    
    @validator('attribute_ids')
    def validate_unique_ids(cls, v):
        """Ensure attribute IDs are unique"""
        if len(v) != len(set(v)):
            raise ValueError('Attribute IDs must be unique')
        return v


class ProductAttributeValueCreateDTO(BaseModel):
    """DTO for creating product attribute value"""
    attribute_id: UUID = Field(..., description="Attribute ID")
    value: Union[str, int, float, bool, List[str]] = Field(..., description="Attribute value")
    
    @validator('value')
    def validate_value_type(cls, v):
        """Basic value type validation"""
        if isinstance(v, list):
            if not all(isinstance(item, str) for item in v):
                raise ValueError('List values must contain only strings')
        return v


class ProductAttributeValueUpdateDTO(BaseModel):
    """DTO for updating product attribute value"""
    value: Union[str, int, float, bool, List[str]] = Field(..., description="Attribute value")


class ProductAttributeValueResponseDTO(BaseModel):
    """DTO for product attribute value response"""
    id: UUID = Field(..., description="Value ID")
    product_id: UUID = Field(..., description="Product ID")
    attribute_id: UUID = Field(..., description="Attribute ID")
    attribute_name: str = Field(..., description="Attribute name")
    attribute_type: AttributeType = Field(..., description="Attribute type")
    value: Union[str, int, float, bool, List[str]] = Field(..., description="Attribute value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True


class AttributeValidationResultDTO(BaseModel):
    """DTO for attribute validation result"""
    is_valid: bool = Field(..., description="Is value valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    normalized_value: Optional[Any] = Field(None, description="Normalized value")


class AttributeStatsDTO(BaseModel):
    """DTO for attribute statistics"""
    total_attributes: int = Field(..., description="Total number of attributes")
    attributes_by_type: Dict[str, int] = Field(..., description="Attributes count by type")
    required_attributes: int = Field(..., description="Number of required attributes")
    filterable_attributes: int = Field(..., description="Number of filterable attributes")
    searchable_attributes: int = Field(..., description="Number of searchable attributes")
    most_used_attributes: List[Dict[str, Any]] = Field(..., description="Most used attributes")


class AttributeGroupDTO(BaseModel):
    """DTO for attribute group"""
    group_name: str = Field(..., description="Group name")
    attributes: List[AttributeResponseDTO] = Field(..., description="Attributes in group")
    display_order: int = Field(default=0, description="Group display order")