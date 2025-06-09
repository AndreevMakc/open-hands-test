from typing import Optional
from pydantic import Field

from .base import BaseEntity
from ..value_objects.common import EntityId, Timestamps
from ..value_objects.category import CategoryPath


class Category(BaseEntity):
    """Category entity"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[EntityId] = None
    path: CategoryPath
    is_active: bool = Field(default=True)
    
    @classmethod
    def create(
        cls,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[EntityId] = None,
        parent_path: Optional[CategoryPath] = None,
        is_active: bool = True,
    ) -> "Category":
        """Create new category"""
        entity_id = EntityId()
        path = CategoryPath.from_parent(parent_path, str(entity_id.value))
        
        return cls(
            id=entity_id,
            timestamps=Timestamps(),
            name=name,
            description=description,
            parent_id=parent_id,
            path=path,
            is_active=is_active,
        )
    
    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> "Category":
        """Update category"""
        updates = {}
        
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if is_active is not None:
            updates["is_active"] = is_active
        
        if updates:
            updates["timestamps"] = self.timestamps.mark_updated()
            return self.model_copy(update=updates)
        
        return self
    
    def move_to_parent(
        self, 
        new_parent_id: Optional[EntityId], 
        new_parent_path: Optional[CategoryPath]
    ) -> "Category":
        """Move category to new parent"""
        new_path = CategoryPath.from_parent(new_parent_path, str(self.id.value))
        
        return self.model_copy(update={
            "parent_id": new_parent_id,
            "path": new_path,
            "timestamps": self.timestamps.mark_updated(),
        })
    
    def deactivate(self) -> "Category":
        """Deactivate category"""
        return self.update(is_active=False)
    
    def activate(self) -> "Category":
        """Activate category"""
        return self.update(is_active=True)
    
    def is_root(self) -> bool:
        """Check if category is root"""
        return self.parent_id is None
    
    def get_depth(self) -> int:
        """Get category depth in hierarchy"""
        return self.path.get_depth()
    
    def is_descendant_of(self, other: "Category") -> bool:
        """Check if this category is descendant of another"""
        return self.path.is_descendant_of(other.path)