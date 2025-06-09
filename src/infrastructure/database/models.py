"""
SQLAlchemy database models for Product Catalog Service
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, 
    Numeric, String, Text, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from ...domain.value_objects.product import ProductStatus
from ...domain.value_objects.attribute import AttributeType

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class CategoryModel(Base, TimestampMixin):
    """Category database model with hierarchical structure using LTREE"""
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Hierarchical path (e.g., "electronics.phones.smartphones")
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # SEO fields
    meta_title: Mapped[Optional[str]] = mapped_column(String(255))
    meta_description: Mapped[Optional[str]] = mapped_column(Text)
    meta_keywords: Mapped[Optional[str]] = mapped_column(Text)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Display order
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    products: Mapped[List["ProductModel"]] = relationship(
        "ProductModel", 
        back_populates="category",
        cascade="all, delete-orphan"
    )
    
    category_attributes: Mapped[List["CategoryAttributeModel"]] = relationship(
        "CategoryAttributeModel",
        back_populates="category",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index('ix_categories_path', 'path'),
        Index('ix_categories_slug', 'slug'),
        Index('ix_categories_active', 'is_active'),
    )

    def __repr__(self) -> str:
        return f"<CategoryModel(id={self.id}, name='{self.name}', path='{self.path}')>"


class AttributeModel(Base, TimestampMixin):
    """Attribute definition model"""
    __tablename__ = "attributes"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Attribute type
    type: Mapped[AttributeType] = mapped_column(
        SQLEnum(AttributeType), 
        nullable=False
    )
    
    # Validation rules (JSON)
    validation_rules: Mapped[Optional[str]] = mapped_column(Text)
    
    # Default value
    default_value: Mapped[Optional[str]] = mapped_column(Text)
    
    # Display properties
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_filterable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_searchable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Display order
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    category_attributes: Mapped[List["CategoryAttributeModel"]] = relationship(
        "CategoryAttributeModel",
        back_populates="attribute",
        cascade="all, delete-orphan"
    )
    
    product_attributes: Mapped[List["ProductAttributeModel"]] = relationship(
        "ProductAttributeModel",
        back_populates="attribute",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index('ix_attributes_slug', 'slug'),
        Index('ix_attributes_type', 'type'),
        Index('ix_attributes_active', 'is_active'),
    )

    def __repr__(self) -> str:
        return f"<AttributeModel(id={self.id}, name='{self.name}', type={self.type})>"


class CategoryAttributeModel(Base, TimestampMixin):
    """Association between categories and attributes"""
    __tablename__ = "category_attributes"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    
    category_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )
    
    attribute_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("attributes.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Override attribute properties for this category
    is_required: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_filterable: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_searchable: Mapped[Optional[bool]] = mapped_column(Boolean)
    
    # Display order within category
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    category: Mapped["CategoryModel"] = relationship(
        "CategoryModel", 
        back_populates="category_attributes"
    )
    
    attribute: Mapped["AttributeModel"] = relationship(
        "AttributeModel", 
        back_populates="category_attributes"
    )

    # Indexes
    __table_args__ = (
        Index('ix_category_attributes_category', 'category_id'),
        Index('ix_category_attributes_attribute', 'attribute_id'),
        Index('ix_category_attributes_unique', 'category_id', 'attribute_id', unique=True),
    )

    def __repr__(self) -> str:
        return f"<CategoryAttributeModel(category_id={self.category_id}, attribute_id={self.attribute_id})>"


class ProductModel(Base, TimestampMixin):
    """Product database model"""
    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    
    # Basic product info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    short_description: Mapped[Optional[str]] = mapped_column(Text)
    
    # SKU
    sku: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    # Pricing
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), 
        nullable=False
    )
    compare_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2)
    )
    cost_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2)
    )
    
    # Inventory
    track_inventory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    inventory_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    allow_backorder: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Physical properties
    weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=8, scale=3))
    length: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=8, scale=3))
    width: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=8, scale=3))
    height: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=8, scale=3))
    
    # Images (array of URLs)
    images: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # SEO fields
    meta_title: Mapped[Optional[str]] = mapped_column(String(255))
    meta_description: Mapped[Optional[str]] = mapped_column(Text)
    meta_keywords: Mapped[Optional[str]] = mapped_column(Text)
    
    # Status and visibility
    status: Mapped[ProductStatus] = mapped_column(
        SQLEnum(ProductStatus), 
        default=ProductStatus.DRAFT,
        nullable=False
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Display order
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Category relationship
    category_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False
    )
    
    # Relationships
    category: Mapped["CategoryModel"] = relationship(
        "CategoryModel", 
        back_populates="products"
    )
    
    product_attributes: Mapped[List["ProductAttributeModel"]] = relationship(
        "ProductAttributeModel",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index('ix_products_slug', 'slug'),
        Index('ix_products_sku', 'sku'),
        Index('ix_products_category', 'category_id'),
        Index('ix_products_status', 'status'),
        Index('ix_products_featured', 'is_featured'),
        Index('ix_products_price', 'price'),
        Index('ix_products_name_search', 'name'),
    )

    def __repr__(self) -> str:
        return f"<ProductModel(id={self.id}, name='{self.name}', sku='{self.sku}')>"


class ProductAttributeModel(Base, TimestampMixin):
    """Product attribute values"""
    __tablename__ = "product_attributes"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    
    product_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    
    attribute_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("attributes.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Attribute value (stored as text, parsed based on attribute type)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relationships
    product: Mapped["ProductModel"] = relationship(
        "ProductModel", 
        back_populates="product_attributes"
    )
    
    attribute: Mapped["AttributeModel"] = relationship(
        "AttributeModel", 
        back_populates="product_attributes"
    )

    # Indexes
    __table_args__ = (
        Index('ix_product_attributes_product', 'product_id'),
        Index('ix_product_attributes_attribute', 'attribute_id'),
        Index('ix_product_attributes_unique', 'product_id', 'attribute_id', unique=True),
        Index('ix_product_attributes_value', 'value'),
    )

    def __repr__(self) -> str:
        return f"<ProductAttributeModel(product_id={self.product_id}, attribute_id={self.attribute_id}, value='{self.value}')>"