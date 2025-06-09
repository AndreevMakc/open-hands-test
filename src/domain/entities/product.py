from typing import Optional, Dict, Any
from pydantic import Field

from .base import BaseEntity
from ..value_objects.common import EntityId, Timestamps, Money, SEOData
from ..value_objects.product import ProductStatus, SKU, ProductImages
from ..value_objects.attribute import AttributeValue


class Product(BaseEntity):
    """Product entity"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sku: SKU
    price: Money
    category_id: EntityId
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)
    images: ProductImages = Field(default_factory=ProductImages)
    seo_data: SEOData = Field(default_factory=SEOData)
    
    @classmethod
    def create(
        cls,
        name: str,
        sku: str,
        price: Money,
        category_id: EntityId,
        description: Optional[str] = None,
        status: ProductStatus = ProductStatus.ACTIVE,
        images: Optional[ProductImages] = None,
        seo_data: Optional[SEOData] = None,
    ) -> "Product":
        """Create new product"""
        return cls(
            id=EntityId(),
            timestamps=Timestamps(),
            name=name,
            description=description,
            sku=SKU(value=sku),
            price=price,
            category_id=category_id,
            status=status,
            images=images or ProductImages(),
            seo_data=seo_data or SEOData(),
        )
    
    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[Money] = None,
        category_id: Optional[EntityId] = None,
        status: Optional[ProductStatus] = None,
        images: Optional[ProductImages] = None,
        seo_data: Optional[SEOData] = None,
    ) -> "Product":
        """Update product"""
        updates = {}
        
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if price is not None:
            updates["price"] = price
        if category_id is not None:
            updates["category_id"] = category_id
        if status is not None:
            updates["status"] = status
        if images is not None:
            updates["images"] = images
        if seo_data is not None:
            updates["seo_data"] = seo_data
        
        if updates:
            updates["timestamps"] = self.timestamps.mark_updated()
            return self.model_copy(update=updates)
        
        return self
    
    def change_status(self, status: ProductStatus) -> "Product":
        """Change product status"""
        return self.update(status=status)
    
    def activate(self) -> "Product":
        """Activate product"""
        return self.change_status(ProductStatus.ACTIVE)
    
    def deactivate(self) -> "Product":
        """Deactivate product"""
        return self.change_status(ProductStatus.INACTIVE)
    
    def archive(self) -> "Product":
        """Archive product"""
        return self.change_status(ProductStatus.ARCHIVED)
    
    def add_image(self, url: str, is_main: bool = False) -> "Product":
        """Add image to product"""
        new_images = self.images.add_image(url, is_main)
        return self.update(images=new_images)
    
    def remove_image(self, url: str) -> "Product":
        """Remove image from product"""
        new_images = self.images.remove_image(url)
        return self.update(images=new_images)
    
    def is_active(self) -> bool:
        """Check if product is active"""
        return self.status == ProductStatus.ACTIVE


class ProductAttributeValue(BaseEntity):
    """Product attribute value entity"""
    product_id: EntityId
    attribute_id: EntityId
    value: AttributeValue
    
    @classmethod
    def create(
        cls,
        product_id: EntityId,
        attribute_id: EntityId,
        value: AttributeValue,
    ) -> "ProductAttributeValue":
        """Create new product attribute value"""
        return cls(
            id=EntityId(),
            timestamps=Timestamps(),
            product_id=product_id,
            attribute_id=attribute_id,
            value=value,
        )
    
    def update_value(self, value: AttributeValue) -> "ProductAttributeValue":
        """Update attribute value"""
        return self.model_copy(update={
            "value": value,
            "timestamps": self.timestamps.mark_updated(),
        })