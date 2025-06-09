from typing import Optional
from pydantic import Field

from .base import BaseEntity
from ..value_objects.common import EntityId, Timestamps
from ..value_objects.attribute import AttributeType, AttributeOptions


class Attribute(BaseEntity):
    """Attribute entity"""
    name: str = Field(..., min_length=1, max_length=255)
    type: AttributeType
    options: AttributeOptions = Field(default_factory=AttributeOptions)
    is_required: bool = Field(default=False)
    
    @classmethod
    def create(
        cls,
        name: str,
        attribute_type: AttributeType,
        options: Optional[AttributeOptions] = None,
        is_required: bool = False,
    ) -> "Attribute":
        """Create new attribute"""
        return cls(
            id=EntityId(),
            timestamps=Timestamps(),
            name=name,
            type=attribute_type,
            options=options or AttributeOptions(),
            is_required=is_required,
        )
    
    def update(
        self,
        name: Optional[str] = None,
        options: Optional[AttributeOptions] = None,
        is_required: Optional[bool] = None,
    ) -> "Attribute":
        """Update attribute"""
        updates = {}
        
        if name is not None:
            updates["name"] = name
        if options is not None:
            updates["options"] = options
        if is_required is not None:
            updates["is_required"] = is_required
        
        if updates:
            updates["timestamps"] = self.timestamps.mark_updated()
            return self.model_copy(update=updates)
        
        return self


class CategoryAttribute(BaseEntity):
    """Category-Attribute relationship entity"""
    category_id: EntityId
    attribute_id: EntityId
    is_inherited: bool = Field(default=False)
    display_order: int = Field(default=0)
    
    @classmethod
    def create(
        cls,
        category_id: EntityId,
        attribute_id: EntityId,
        is_inherited: bool = False,
        display_order: int = 0,
    ) -> "CategoryAttribute":
        """Create new category-attribute relationship"""
        return cls(
            id=EntityId(),
            timestamps=Timestamps(),
            category_id=category_id,
            attribute_id=attribute_id,
            is_inherited=is_inherited,
            display_order=display_order,
        )
    
    def update_order(self, display_order: int) -> "CategoryAttribute":
        """Update display order"""
        return self.model_copy(update={
            "display_order": display_order,
            "timestamps": self.timestamps.mark_updated(),
        })