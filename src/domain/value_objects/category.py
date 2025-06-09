from typing import Optional
from pydantic import BaseModel, Field


class CategoryPath(BaseModel):
    """Value object for category hierarchy path"""
    path: str = Field(..., description="LTREE path for hierarchy")
    
    @classmethod
    def root(cls) -> "CategoryPath":
        """Create root category path"""
        return cls(path="")
    
    @classmethod
    def from_parent(cls, parent_path: Optional["CategoryPath"], category_id: str) -> "CategoryPath":
        """Create path from parent path and category ID"""
        if parent_path is None or parent_path.path == "":
            return cls(path=category_id)
        return cls(path=f"{parent_path.path}.{category_id}")
    
    def get_parent_path(self) -> Optional["CategoryPath"]:
        """Get parent path"""
        if "." not in self.path:
            return None
        parent = ".".join(self.path.split(".")[:-1])
        return CategoryPath(path=parent) if parent else None
    
    def get_depth(self) -> int:
        """Get category depth in hierarchy"""
        if not self.path:
            return 0
        return len(self.path.split("."))
    
    def is_descendant_of(self, other: "CategoryPath") -> bool:
        """Check if this path is descendant of another"""
        if not other.path:
            return True
        return self.path.startswith(f"{other.path}.")
    
    def __str__(self) -> str:
        return self.path