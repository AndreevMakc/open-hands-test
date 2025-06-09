from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ProductStatus(str, Enum):
    """Product status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class SKU(BaseModel):
    """Value object for product SKU"""
    value: str = Field(..., min_length=1, max_length=100, description="Product SKU")
    
    def __str__(self) -> str:
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)


class ProductImages(BaseModel):
    """Value object for product images"""
    main_image: Optional[str] = Field(None, description="Main product image URL")
    gallery: list[str] = Field(default_factory=list, description="Additional images")
    
    def add_image(self, url: str, is_main: bool = False) -> "ProductImages":
        """Add image to product"""
        if is_main:
            return self.model_copy(update={"main_image": url})
        
        new_gallery = self.gallery.copy()
        if url not in new_gallery:
            new_gallery.append(url)
        return self.model_copy(update={"gallery": new_gallery})
    
    def remove_image(self, url: str) -> "ProductImages":
        """Remove image from product"""
        updates = {}
        
        if self.main_image == url:
            updates["main_image"] = None
        
        if url in self.gallery:
            new_gallery = [img for img in self.gallery if img != url]
            updates["gallery"] = new_gallery
        
        return self.model_copy(update=updates) if updates else self
    
    def get_all_images(self) -> list[str]:
        """Get all product images"""
        images = []
        if self.main_image:
            images.append(self.main_image)
        images.extend(self.gallery)
        return images