"""
Attribute Use Cases

Business logic for attribute management operations.
"""

import re
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime

from ...domain.entities.attribute import Attribute, AttributeType
from ...domain.value_objects.common import EntityId
from ...domain.repositories.attribute_repository import AttributeRepository
from ...domain.repositories.category import CategoryRepository
from ..dtos.attribute_dto import (
    AttributeCreateDTO,
    AttributeUpdateDTO,
    AttributeResponseDTO,
    AttributeListDTO,
    AttributeFilterDTO,
    CategoryAttributeDTO,
    CategoryAttributeCreateDTO,
    ProductAttributeValueCreateDTO,
    ProductAttributeValueUpdateDTO,
    ProductAttributeValueResponseDTO,
    AttributeValidationResultDTO,
    AttributeStatsDTO,
    AttributeGroupDTO
)


class AttributeUseCases:
    """Use cases for attribute management"""
    
    def __init__(
        self,
        attribute_repository: AttributeRepository,
        category_repository: CategoryRepository
    ):
        self._attribute_repository = attribute_repository
        self._category_repository = category_repository
    
    async def create_attribute(self, attribute_data: AttributeCreateDTO) -> AttributeResponseDTO:
        """Create a new attribute"""
        # Check if attribute name is unique
        existing_attribute = await self._attribute_repository.get_by_name(attribute_data.name)
        if existing_attribute:
            raise ValueError(f"Attribute with name '{attribute_data.name}' already exists")
        
        # Validate attribute configuration
        self._validate_attribute_config(attribute_data)
        
        # Create attribute entity
        attribute = Attribute(
            id=EntityId(),
            name=attribute_data.name,
            description=attribute_data.description,
            type=attribute_data.type,
            unit=attribute_data.unit,
            is_required=attribute_data.is_required,
            is_filterable=attribute_data.is_filterable,
            is_searchable=attribute_data.is_searchable,
            validation_rules={
                'min_value': attribute_data.min_value,
                'max_value': attribute_data.max_value,
                'min_length': attribute_data.min_length,
                'max_length': attribute_data.max_length,
                'allowed_values': attribute_data.allowed_values,
                'regex_pattern': attribute_data.regex_pattern
            },
            display_order=attribute_data.display_order,
            group_name=attribute_data.group_name
        )
        
        # Save attribute
        saved_attribute = await self._attribute_repository.create(attribute)
        
        # Convert to response DTO
        return await self._attribute_to_response_dto(saved_attribute)
    
    async def get_attribute_by_id(self, attribute_id: UUID) -> Optional[AttributeResponseDTO]:
        """Get attribute by ID"""
        attribute = await self._attribute_repository.get_by_id(EntityId(attribute_id))
        if not attribute:
            return None
        
        return await self._attribute_to_response_dto(attribute)
    
    async def get_attribute_by_name(self, name: str) -> Optional[AttributeResponseDTO]:
        """Get attribute by name"""
        attribute = await self._attribute_repository.get_by_name(name)
        if not attribute:
            return None
        
        return await self._attribute_to_response_dto(attribute)
    
    async def update_attribute(
        self, 
        attribute_id: UUID, 
        update_data: AttributeUpdateDTO
    ) -> Optional[AttributeResponseDTO]:
        """Update an existing attribute"""
        attribute = await self._attribute_repository.get_by_id(EntityId(attribute_id))
        if not attribute:
            return None
        
        # Check name uniqueness if being updated
        if update_data.name and update_data.name != attribute.name:
            existing_attribute = await self._attribute_repository.get_by_name(update_data.name)
            if existing_attribute:
                raise ValueError(f"Attribute with name '{update_data.name}' already exists")
            attribute.name = update_data.name
        
        # Update attribute fields
        if update_data.description is not None:
            attribute.description = update_data.description
        
        if update_data.unit is not None:
            attribute.unit = update_data.unit
        
        if update_data.is_required is not None:
            attribute.is_required = update_data.is_required
        
        if update_data.is_filterable is not None:
            attribute.is_filterable = update_data.is_filterable
        
        if update_data.is_searchable is not None:
            attribute.is_searchable = update_data.is_searchable
        
        if update_data.display_order is not None:
            attribute.display_order = update_data.display_order
        
        if update_data.group_name is not None:
            attribute.group_name = update_data.group_name
        
        # Update validation rules
        validation_rules = attribute.validation_rules.copy()
        if update_data.min_value is not None:
            validation_rules['min_value'] = update_data.min_value
        if update_data.max_value is not None:
            validation_rules['max_value'] = update_data.max_value
        if update_data.min_length is not None:
            validation_rules['min_length'] = update_data.min_length
        if update_data.max_length is not None:
            validation_rules['max_length'] = update_data.max_length
        if update_data.allowed_values is not None:
            validation_rules['allowed_values'] = update_data.allowed_values
        if update_data.regex_pattern is not None:
            validation_rules['regex_pattern'] = update_data.regex_pattern
        
        attribute.validation_rules = validation_rules
        
        # Mark as updated
        attribute.timestamps = attribute.timestamps.mark_updated()
        
        # Save updated attribute
        updated_attribute = await self._attribute_repository.update(attribute)
        return await self._attribute_to_response_dto(updated_attribute)
    
    async def delete_attribute(self, attribute_id: UUID) -> bool:
        """Delete an attribute"""
        attribute = await self._attribute_repository.get_by_id(EntityId(attribute_id))
        if not attribute:
            return False
        
        # Check if attribute is used by any products
        usage_count = await self._attribute_repository.get_usage_count(EntityId(attribute_id))
        if usage_count > 0:
            raise ValueError(f"Cannot delete attribute: it is used by {usage_count} products")
        
        await self._attribute_repository.delete(EntityId(attribute_id))
        return True
    
    async def list_attributes(self, filters: AttributeFilterDTO) -> AttributeListDTO:
        """List attributes with filtering and pagination"""
        # Build filter criteria
        filter_criteria = {}
        
        if filters.type:
            filter_criteria['type'] = filters.type
        
        if filters.is_required is not None:
            filter_criteria['is_required'] = filters.is_required
        
        if filters.is_filterable is not None:
            filter_criteria['is_filterable'] = filters.is_filterable
        
        if filters.is_searchable is not None:
            filter_criteria['is_searchable'] = filters.is_searchable
        
        if filters.group_name:
            filter_criteria['group_name'] = filters.group_name
        
        if filters.search:
            filter_criteria['search'] = filters.search
        
        # Get attributes with pagination
        attributes, total = await self._attribute_repository.list_with_filters(
            filters=filter_criteria,
            page=filters.page,
            size=filters.size,
            sort_by=filters.sort_by,
            sort_order=filters.sort_order
        )
        
        # Convert to response DTOs
        attribute_dtos = []
        for attribute in attributes:
            attribute_dto = await self._attribute_to_response_dto(attribute)
            attribute_dtos.append(attribute_dto)
        
        # Calculate pagination info
        pages = (total + filters.size - 1) // filters.size
        has_next = filters.page < pages
        has_prev = filters.page > 1
        
        return AttributeListDTO(
            attributes=attribute_dtos,
            total=total,
            page=filters.page,
            size=filters.size,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
    
    async def assign_attributes_to_category(
        self, 
        category_id: UUID, 
        assignment_data: CategoryAttributeCreateDTO
    ) -> List[CategoryAttributeDTO]:
        """Assign attributes to a category"""
        # Verify category exists
        category = await self._category_repository.get_by_id(EntityId(category_id))
        if not category:
            raise ValueError(f"Category with ID {category_id} not found")
        
        # Verify all attributes exist
        attribute_ids = [EntityId(aid) for aid in assignment_data.attribute_ids]
        for attr_id in attribute_ids:
            attribute = await self._attribute_repository.get_by_id(attr_id)
            if not attribute:
                raise ValueError(f"Attribute with ID {attr_id.value} not found")
        
        # Assign attributes to category
        assignments = await self._attribute_repository.assign_to_category(
            category_id=EntityId(category_id),
            attribute_ids=attribute_ids,
            inherit_to_children=assignment_data.inherit_to_children
        )
        
        # Convert to DTOs
        return [
            CategoryAttributeDTO(
                category_id=assignment.category_id.value,
                attribute_id=assignment.attribute_id.value,
                is_inherited=assignment.is_inherited,
                display_order=assignment.display_order
            )
            for assignment in assignments
        ]
    
    async def get_category_attributes(self, category_id: UUID) -> List[AttributeResponseDTO]:
        """Get all attributes assigned to a category"""
        attributes = await self._attribute_repository.get_by_category(EntityId(category_id))
        
        return [
            await self._attribute_to_response_dto(attribute)
            for attribute in attributes
        ]
    
    async def validate_attribute_value(
        self, 
        attribute_id: UUID, 
        value: Any
    ) -> AttributeValidationResultDTO:
        """Validate an attribute value"""
        attribute = await self._attribute_repository.get_by_id(EntityId(attribute_id))
        if not attribute:
            return AttributeValidationResultDTO(
                is_valid=False,
                errors=["Attribute not found"],
                warnings=[],
                normalized_value=None
            )
        
        errors = []
        warnings = []
        normalized_value = value
        
        # Type validation
        if attribute.type == AttributeType.STRING:
            if not isinstance(value, str):
                errors.append("Value must be a string")
            else:
                # Length validation
                if attribute.validation_rules.get('min_length'):
                    if len(value) < attribute.validation_rules['min_length']:
                        errors.append(f"Value must be at least {attribute.validation_rules['min_length']} characters")
                
                if attribute.validation_rules.get('max_length'):
                    if len(value) > attribute.validation_rules['max_length']:
                        errors.append(f"Value must be at most {attribute.validation_rules['max_length']} characters")
                
                # Regex validation
                if attribute.validation_rules.get('regex_pattern'):
                    if not re.match(attribute.validation_rules['regex_pattern'], value):
                        errors.append("Value does not match required pattern")
        
        elif attribute.type == AttributeType.INTEGER:
            try:
                normalized_value = int(value)
                # Range validation
                if attribute.validation_rules.get('min_value') is not None:
                    if normalized_value < attribute.validation_rules['min_value']:
                        errors.append(f"Value must be at least {attribute.validation_rules['min_value']}")
                
                if attribute.validation_rules.get('max_value') is not None:
                    if normalized_value > attribute.validation_rules['max_value']:
                        errors.append(f"Value must be at most {attribute.validation_rules['max_value']}")
            except (ValueError, TypeError):
                errors.append("Value must be an integer")
        
        elif attribute.type == AttributeType.FLOAT:
            try:
                normalized_value = float(value)
                # Range validation
                if attribute.validation_rules.get('min_value') is not None:
                    if normalized_value < attribute.validation_rules['min_value']:
                        errors.append(f"Value must be at least {attribute.validation_rules['min_value']}")
                
                if attribute.validation_rules.get('max_value') is not None:
                    if normalized_value > attribute.validation_rules['max_value']:
                        errors.append(f"Value must be at most {attribute.validation_rules['max_value']}")
            except (ValueError, TypeError):
                errors.append("Value must be a number")
        
        elif attribute.type == AttributeType.BOOLEAN:
            if not isinstance(value, bool):
                if isinstance(value, str):
                    if value.lower() in ('true', '1', 'yes', 'on'):
                        normalized_value = True
                    elif value.lower() in ('false', '0', 'no', 'off'):
                        normalized_value = False
                    else:
                        errors.append("Value must be a boolean")
                else:
                    errors.append("Value must be a boolean")
        
        elif attribute.type == AttributeType.ENUM:
            allowed_values = attribute.validation_rules.get('allowed_values', [])
            if value not in allowed_values:
                errors.append(f"Value must be one of: {', '.join(allowed_values)}")
        
        elif attribute.type == AttributeType.DATE:
            if isinstance(value, str):
                try:
                    normalized_value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    errors.append("Value must be a valid ISO date format")
            elif not isinstance(value, datetime):
                errors.append("Value must be a date")
        
        return AttributeValidationResultDTO(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            normalized_value=normalized_value
        )
    
    async def get_attribute_stats(self) -> AttributeStatsDTO:
        """Get attribute statistics"""
        stats = await self._attribute_repository.get_statistics()
        
        return AttributeStatsDTO(
            total_attributes=stats.get('total', 0),
            attributes_by_type=stats.get('by_type', {}),
            required_attributes=stats.get('required', 0),
            filterable_attributes=stats.get('filterable', 0),
            searchable_attributes=stats.get('searchable', 0),
            most_used_attributes=stats.get('most_used', [])
        )
    
    async def get_attributes_by_group(self) -> List[AttributeGroupDTO]:
        """Get attributes grouped by group name"""
        attributes = await self._attribute_repository.get_all()
        
        # Group attributes
        groups = {}
        for attribute in attributes:
            group_name = attribute.group_name or "Default"
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(attribute)
        
        # Convert to DTOs
        group_dtos = []
        for group_name, group_attributes in groups.items():
            # Sort by display order
            group_attributes.sort(key=lambda a: a.display_order)
            
            group_dto = AttributeGroupDTO(
                group_name=group_name,
                attributes=[
                    await self._attribute_to_response_dto(attr)
                    for attr in group_attributes
                ],
                display_order=min(attr.display_order for attr in group_attributes) if group_attributes else 0
            )
            group_dtos.append(group_dto)
        
        # Sort groups by display order
        group_dtos.sort(key=lambda g: g.display_order)
        
        return group_dtos
    
    def _validate_attribute_config(self, attribute_data: AttributeCreateDTO) -> None:
        """Validate attribute configuration"""
        # Enum type must have allowed values
        if attribute_data.type == AttributeType.ENUM and not attribute_data.allowed_values:
            raise ValueError("Enum type attributes must have allowed_values")
        
        # Numeric types validation
        if attribute_data.type in [AttributeType.INTEGER, AttributeType.FLOAT]:
            if attribute_data.min_value is not None and attribute_data.max_value is not None:
                if attribute_data.min_value >= attribute_data.max_value:
                    raise ValueError("min_value must be less than max_value")
        
        # String type validation
        if attribute_data.type == AttributeType.STRING:
            if attribute_data.min_length is not None and attribute_data.max_length is not None:
                if attribute_data.min_length >= attribute_data.max_length:
                    raise ValueError("min_length must be less than max_length")
        
        # Regex pattern validation
        if attribute_data.regex_pattern:
            try:
                re.compile(attribute_data.regex_pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
    
    async def _attribute_to_response_dto(self, attribute: Attribute) -> AttributeResponseDTO:
        """Convert attribute entity to response DTO"""
        # Get usage statistics
        categories_count = await self._attribute_repository.get_categories_count(attribute.id)
        products_count = await self._attribute_repository.get_usage_count(attribute.id)
        
        return AttributeResponseDTO(
            id=attribute.id.value,
            name=attribute.name,
            description=attribute.description,
            type=attribute.type,
            unit=attribute.unit,
            is_required=attribute.is_required,
            is_filterable=attribute.is_filterable,
            is_searchable=attribute.is_searchable,
            min_value=attribute.validation_rules.get('min_value'),
            max_value=attribute.validation_rules.get('max_value'),
            min_length=attribute.validation_rules.get('min_length'),
            max_length=attribute.validation_rules.get('max_length'),
            allowed_values=attribute.validation_rules.get('allowed_values', []),
            regex_pattern=attribute.validation_rules.get('regex_pattern'),
            display_order=attribute.display_order,
            group_name=attribute.group_name,
            created_at=attribute.timestamps.created_at,
            updated_at=attribute.timestamps.updated_at,
            categories_count=categories_count,
            products_count=products_count
        )