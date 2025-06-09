"""
Attribute repository implementation using SQLAlchemy
"""
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, and_, or_, func, desc, asc, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from ...domain.entities.attribute import Attribute, AttributeType
from ...domain.repositories.attribute_repository import AttributeRepository
from ...domain.value_objects.common import EntityId, Timestamps
from ..database.models import AttributeModel, CategoryAttributeModel, ProductAttributeModel


class SQLAlchemyAttributeRepository(AttributeRepository):
    """SQLAlchemy implementation of AttributeRepository"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, attribute: Attribute) -> Attribute:
        """Create a new attribute"""
        model = self._create_model_from_entity(attribute)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return await self._model_to_entity(model)
    
    async def get_by_id(self, attribute_id: EntityId) -> Optional[Attribute]:
        """Get attribute by ID"""
        stmt = select(AttributeModel).where(AttributeModel.id == attribute_id.value)
        
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return await self._model_to_entity(model) if model else None
    
    async def get_by_name(self, name: str) -> Optional[Attribute]:
        """Get attribute by name"""
        stmt = select(AttributeModel).where(AttributeModel.name == name)
        
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return await self._model_to_entity(model) if model else None
    
    async def update(self, attribute: Attribute) -> Attribute:
        """Update an existing attribute"""
        model = await self._session.get(AttributeModel, attribute.id.value)
        if not model:
            raise ValueError(f"Attribute with ID {attribute.id.value} not found")
        
        self._update_model_from_entity(model, attribute)
        await self._session.flush()
        await self._session.refresh(model)
        return await self._model_to_entity(model)
    
    async def delete(self, attribute_id: EntityId) -> bool:
        """Delete attribute by ID"""
        model = await self._session.get(AttributeModel, attribute_id.value)
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
    
    async def list_with_filters(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        size: int = 20,
        sort_by: str = "display_order",
        sort_order: str = "asc"
    ) -> Tuple[List[Attribute], int]:
        """List attributes with filters and pagination"""
        conditions = []
        
        # Apply filters
        if 'type' in filters:
            conditions.append(AttributeModel.type == filters['type'])
        
        if 'is_required' in filters:
            conditions.append(AttributeModel.is_required == filters['is_required'])
        
        if 'is_filterable' in filters:
            conditions.append(AttributeModel.is_filterable == filters['is_filterable'])
        
        if 'is_searchable' in filters:
            conditions.append(AttributeModel.is_searchable == filters['is_searchable'])
        
        if 'group_name' in filters:
            conditions.append(AttributeModel.group_name == filters['group_name'])
        
        if 'search' in filters:
            search_term = f"%{filters['search']}%"
            conditions.append(
                or_(
                    AttributeModel.name.ilike(search_term),
                    AttributeModel.description.ilike(search_term)
                )
            )
        
        # Count total
        count_stmt = select(func.count(AttributeModel.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Get attributes
        stmt = select(AttributeModel)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Sorting
        sort_column = getattr(AttributeModel, sort_by, AttributeModel.display_order)
        if sort_order.lower() == "desc":
            stmt = stmt.order_by(desc(sort_column))
        else:
            stmt = stmt.order_by(asc(sort_column))
        
        # Pagination
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        attributes = [await self._model_to_entity(model) for model in models]
        
        return attributes, total
    
    async def get_all(self) -> List[Attribute]:
        """Get all attributes"""
        stmt = select(AttributeModel).order_by(AttributeModel.display_order, AttributeModel.name)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [await self._model_to_entity(model) for model in models]
    
    async def get_by_category(self, category_id: EntityId) -> List[Attribute]:
        """Get attributes assigned to a category"""
        stmt = select(AttributeModel).join(
            CategoryAttributeModel,
            CategoryAttributeModel.attribute_id == AttributeModel.id
        ).where(
            CategoryAttributeModel.category_id == category_id.value
        ).order_by(
            CategoryAttributeModel.display_order,
            AttributeModel.display_order,
            AttributeModel.name
        )
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [await self._model_to_entity(model) for model in models]
    
    async def assign_to_category(
        self,
        category_id: EntityId,
        attribute_ids: List[EntityId],
        inherit_to_children: bool = False
    ) -> List[Any]:  # CategoryAttribute entity would be defined
        """Assign attributes to a category"""
        assignments = []
        
        for i, attribute_id in enumerate(attribute_ids):
            # Check if assignment already exists
            existing_stmt = select(CategoryAttributeModel).where(
                and_(
                    CategoryAttributeModel.category_id == category_id.value,
                    CategoryAttributeModel.attribute_id == attribute_id.value
                )
            )
            existing_result = await self._session.execute(existing_stmt)
            existing = existing_result.scalar_one_or_none()
            
            if not existing:
                assignment = CategoryAttributeModel(
                    category_id=category_id.value,
                    attribute_id=attribute_id.value,
                    is_inherited=False,
                    display_order=i
                )
                self._session.add(assignment)
                assignments.append(assignment)
        
        await self._session.flush()
        
        # TODO: Handle inherit_to_children logic
        # This would require getting child categories and creating assignments
        
        return assignments
    
    async def get_usage_count(self, attribute_id: EntityId) -> int:
        """Get number of products using this attribute"""
        stmt = select(func.count(ProductAttributeModel.id)).where(
            ProductAttributeModel.attribute_id == attribute_id.value
        )
        
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def get_categories_count(self, attribute_id: EntityId) -> int:
        """Get number of categories using this attribute"""
        stmt = select(func.count(CategoryAttributeModel.id)).where(
            CategoryAttributeModel.attribute_id == attribute_id.value
        )
        
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get attribute statistics"""
        # Total attributes
        total_stmt = select(func.count(AttributeModel.id))
        total_result = await self._session.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # Attributes by type
        type_stmt = select(
            AttributeModel.type,
            func.count(AttributeModel.id)
        ).group_by(AttributeModel.type)
        
        type_result = await self._session.execute(type_stmt)
        type_counts = {row[0].value: row[1] for row in type_result.fetchall()}
        
        # Required attributes
        required_stmt = select(func.count(AttributeModel.id)).where(
            AttributeModel.is_required == True
        )
        required_result = await self._session.execute(required_stmt)
        required_count = required_result.scalar() or 0
        
        # Filterable attributes
        filterable_stmt = select(func.count(AttributeModel.id)).where(
            AttributeModel.is_filterable == True
        )
        filterable_result = await self._session.execute(filterable_stmt)
        filterable_count = filterable_result.scalar() or 0
        
        # Searchable attributes
        searchable_stmt = select(func.count(AttributeModel.id)).where(
            AttributeModel.is_searchable == True
        )
        searchable_result = await self._session.execute(searchable_stmt)
        searchable_count = searchable_result.scalar() or 0
        
        # Most used attributes
        most_used_stmt = select(
            AttributeModel.name,
            func.count(ProductAttributeModel.id).label('usage_count')
        ).select_from(
            AttributeModel.__table__.outerjoin(ProductAttributeModel.__table__)
        ).group_by(
            AttributeModel.id, AttributeModel.name
        ).order_by(
            desc('usage_count')
        ).limit(10)
        
        most_used_result = await self._session.execute(most_used_stmt)
        most_used = [
            {'name': row[0], 'usage_count': row[1]}
            for row in most_used_result.fetchall()
        ]
        
        return {
            'total': total,
            'by_type': type_counts,
            'required': required_count,
            'filterable': filterable_count,
            'searchable': searchable_count,
            'most_used': most_used
        }
    
    def _create_model_from_entity(self, attribute: Attribute) -> AttributeModel:
        """Create database model from domain entity"""
        return AttributeModel(
            id=attribute.id.value,
            name=attribute.name,
            description=attribute.description,
            type=attribute.type,
            unit=attribute.unit,
            is_required=attribute.is_required,
            is_filterable=attribute.is_filterable,
            is_searchable=attribute.is_searchable,
            validation_rules=attribute.validation_rules,
            display_order=attribute.display_order,
            group_name=attribute.group_name,
            created_at=attribute.timestamps.created_at,
            updated_at=attribute.timestamps.updated_at
        )
    
    def _update_model_from_entity(self, model: AttributeModel, attribute: Attribute) -> None:
        """Update database model from domain entity"""
        model.name = attribute.name
        model.description = attribute.description
        model.type = attribute.type
        model.unit = attribute.unit
        model.is_required = attribute.is_required
        model.is_filterable = attribute.is_filterable
        model.is_searchable = attribute.is_searchable
        model.validation_rules = attribute.validation_rules
        model.display_order = attribute.display_order
        model.group_name = attribute.group_name
        model.updated_at = attribute.timestamps.updated_at
    
    async def _model_to_entity(self, model: AttributeModel) -> Attribute:
        """Convert database model to domain entity"""
        return Attribute(
            id=EntityId(model.id),
            name=model.name,
            description=model.description,
            type=model.type,
            unit=model.unit,
            is_required=model.is_required,
            is_filterable=model.is_filterable,
            is_searchable=model.is_searchable,
            validation_rules=model.validation_rules or {},
            display_order=model.display_order,
            group_name=model.group_name,
            timestamps=Timestamps(
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        )