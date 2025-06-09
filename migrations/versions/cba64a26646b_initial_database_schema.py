"""Initial database schema

Revision ID: cba64a26646b
Revises: 
Create Date: 2025-06-09 18:42:50.746825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'cba64a26646b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create categories table
    op.create_table('categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('path', sa.String(length=500), nullable=False),
        sa.Column('meta_title', sa.String(length=255), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('meta_keywords', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_categories_active', 'categories', ['is_active'], unique=False)
    op.create_index('ix_categories_path', 'categories', ['path'], unique=False)
    op.create_index('ix_categories_slug', 'categories', ['slug'], unique=False)
    op.create_unique_constraint(None, 'categories', ['slug'])

    # Create attributes table
    op.create_table('attributes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Enum('STRING', 'INTEGER', 'DECIMAL', 'BOOLEAN', 'DATE', 'DATETIME', 'TEXT', 'SELECT', 'MULTISELECT', name='attributetype'), nullable=False),
        sa.Column('validation_rules', sa.Text(), nullable=True),
        sa.Column('default_value', sa.Text(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('is_filterable', sa.Boolean(), nullable=False),
        sa.Column('is_searchable', sa.Boolean(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_attributes_active', 'attributes', ['is_active'], unique=False)
    op.create_index('ix_attributes_slug', 'attributes', ['slug'], unique=False)
    op.create_index('ix_attributes_type', 'attributes', ['type'], unique=False)
    op.create_unique_constraint(None, 'attributes', ['slug'])

    # Create products table
    op.create_table('products',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('compare_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('cost_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('track_inventory', sa.Boolean(), nullable=False),
        sa.Column('inventory_quantity', sa.Integer(), nullable=False),
        sa.Column('allow_backorder', sa.Boolean(), nullable=False),
        sa.Column('weight', sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column('length', sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column('width', sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column('height', sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column('images', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('meta_title', sa.String(length=255), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('meta_keywords', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'ACTIVE', 'INACTIVE', 'ARCHIVED', name='productstatus'), nullable=False),
        sa.Column('is_featured', sa.Boolean(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_category', 'products', ['category_id'], unique=False)
    op.create_index('ix_products_featured', 'products', ['is_featured'], unique=False)
    op.create_index('ix_products_name_search', 'products', ['name'], unique=False)
    op.create_index('ix_products_price', 'products', ['price'], unique=False)
    op.create_index('ix_products_sku', 'products', ['sku'], unique=False)
    op.create_index('ix_products_slug', 'products', ['slug'], unique=False)
    op.create_index('ix_products_status', 'products', ['status'], unique=False)
    op.create_unique_constraint(None, 'products', ['sku'])
    op.create_unique_constraint(None, 'products', ['slug'])

    # Create category_attributes table
    op.create_table('category_attributes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attribute_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=True),
        sa.Column('is_filterable', sa.Boolean(), nullable=True),
        sa.Column('is_searchable', sa.Boolean(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['attribute_id'], ['attributes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_category_attributes_attribute', 'category_attributes', ['attribute_id'], unique=False)
    op.create_index('ix_category_attributes_category', 'category_attributes', ['category_id'], unique=False)
    op.create_index('ix_category_attributes_unique', 'category_attributes', ['category_id', 'attribute_id'], unique=True)

    # Create product_attributes table
    op.create_table('product_attributes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attribute_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['attribute_id'], ['attributes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_product_attributes_attribute', 'product_attributes', ['attribute_id'], unique=False)
    op.create_index('ix_product_attributes_product', 'product_attributes', ['product_id'], unique=False)
    op.create_index('ix_product_attributes_unique', 'product_attributes', ['product_id', 'attribute_id'], unique=True)
    op.create_index('ix_product_attributes_value', 'product_attributes', ['value'], unique=False)


def downgrade() -> None:
    op.drop_table('product_attributes')
    op.drop_table('category_attributes')
    op.drop_table('products')
    op.drop_table('attributes')
    op.drop_table('categories')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS productstatus')
    op.execute('DROP TYPE IF EXISTS attributetype')
