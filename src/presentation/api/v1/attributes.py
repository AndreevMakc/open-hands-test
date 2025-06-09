"""
Attribute API endpoints

REST API for attribute management operations.
"""

from typing import List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ....application.use_cases.attribute_use_cases import AttributeUseCases
from ....application.dtos.attribute_dto import (
    AttributeCreateDTO,
    AttributeUpdateDTO,
    AttributeResponseDTO,
    AttributeListDTO,
    AttributeFilterDTO,
    CategoryAttributeCreateDTO,
    CategoryAttributeDTO,
    AttributeValidationResultDTO,
    AttributeStatsDTO,
    AttributeGroupDTO
)
from ....infrastructure.database.connection import get_db_session
from ....infrastructure.repositories.attribute_repository import SQLAlchemyAttributeRepository
from ....infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository


router = APIRouter(prefix="/attributes", tags=["attributes"])


async def get_attribute_use_cases(session=Depends(get_db_session)) -> AttributeUseCases:
    """Dependency to get AttributeUseCases instance"""
    attribute_repository = SQLAlchemyAttributeRepository(session)
    category_repository = SQLAlchemyCategoryRepository(session)
    return AttributeUseCases(attribute_repository, category_repository)


@router.post(
    "/",
    response_model=AttributeResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new attribute",
    description="Create a new attribute with the provided configuration"
)
async def create_attribute(
    attribute_data: AttributeCreateDTO,
    use_cases: AttributeUseCases = Depends(get_attribute_use_cases)
) -> AttributeResponseDTO:
    """Create a new attribute"""
    try:
        return await use_cases.create_attribute(attribute_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create attribute: {str(e)}"
        )


@router.get(
    "/",
    response_model=AttributeListDTO,
    summary="List attributes",
    description="Get a paginated list of attributes with optional filtering"
)
async def list_attributes(
    type: Optional[str] = Query(None, description="Filter by attribute type"),
    is_required: Optional[bool] = Query(None, description="Filter by required status"),
    is_filterable: Optional[bool] = Query(None, description="Filter by filterable status"),
    is_searchable: Optional[bool] = Query(None, description="Filter by searchable status"),
    group_name: Optional[str] = Query(None, description="Filter by group name"),
    search: Optional[str] = Query(None, min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: str = Query("display_order", description="Sort field"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    use_cases: AttributeUseCases = Depends(get_attribute_use_cases)
) -> AttributeListDTO:
    """List attributes with filtering and pagination"""
    try:
        # Convert type string to enum if provided
        type_enum = None
        if type:
            from ....domain.entities.attribute import AttributeType
            try:
                type_enum = AttributeType(type.upper())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid attribute type: {type}"
                )
        
        filters = AttributeFilterDTO(
            type=type_enum,
            is_required=is_required,
            is_filterable=is_filterable,
            is_searchable=is_searchable,
            group_name=group_name,
            search=search,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return await use_cases.list_attributes(filters)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list attributes: {str(e)}"
        )


@router.get(
    "/groups",
    response_model=List[AttributeGroupDTO],
    summary="Get attributes grouped by group name",
    description="Get all attributes organized by their group names"
)
async def get_attributes_by_group(
    use_cases: AttributeUseCases = Depends(get_attribute_use_cases)
) -> List[AttributeGroupDTO]:
    """Get attributes grouped by group name"""
    try:
        return await use_cases.get_attributes_by_group()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attribute groups: {str(e)}"
        )


@router.get(
    "/{attribute_id}",
    response_model=AttributeResponseDTO,
    summary="Get attribute by ID",
    description="Retrieve a specific attribute by its ID"
)
async def get_attribute(
    attribute_id: UUID,
    use_cases: AttributeUseCases = Depends(get_attribute_use_cases)
) -> AttributeResponseDTO:
    """Get attribute by ID"""
    try:
        attribute = await use_cases.get_attribute_by_id(attribute_id)
        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attribute with ID {attribute_id} not found"
            )
        return attribute
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attribute: {str(e)}"
        )


@router.get(
    "/name/{name}",
    response_model=AttributeResponseDTO,
    summary="Get attribute by name",
    description="Retrieve a specific attribute by its name"
)
async def get_attribute_by_name(
    name: str,
    use_cases: AttributeUseCases = Depends(get_attribute_use_cases)
) -> AttributeResponseDTO:
    """Get attribute by name"""
    try:
        attribute = await use_cases.get_attribute_by_name(name)
        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attribute with name '{name}' not found"
            )
        return attribute
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attribute: {str(e)}"
        )


@router.put(
    "/{attribute_id}",
    response_model=AttributeResponseDTO,
    summary="Update attribute",
    description="Update an existing attribute"
)
async def update_attribute(
    attribute_id: UUID,
    update_data: AttributeUpdateDTO,
    use_cases: AttributeUseCases = Depends(get_attribute_use_cases)
) -> AttributeResponseDTO:
    """Update an existing attribute"""
    try:
        attribute = await use_cases.update_attribute(attribute_id, update_data)
        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attribute with ID {attribute_id} not found"
            )
        return attribute
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update attribute: {str(e)}"
        )


@router.delete(
    "/{attribute_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete attribute",
    description="Delete an attribute by its ID"
)
async def delete_attribute(
    attribute_id: UUID,
    use_cases: AttributeUseCases = Depends(get_attribute_use_cases)
):
    """Delete an attribute"""
    try:
        success = await use_cases.delete_attribute(attribute_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attribute with ID {attribute_id} not found"
            )
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete attribute: {str(e)}"
        )


@router.post(
    "/{attribute_id}/validate",
    response_model=AttributeValidationResultDTO,
    summary="Validate attribute value",
    description="Validate a value against an attribute's validation rules"
)
async def validate_attribute_value(
    attribute_id: UUID,
    value: Any,
    use_cases: AttributeUseCases = Depends(get_attribute_use_cases)
) -> AttributeValidationResultDTO:
    """Validate an attribute value"""
    try:
        return await use_cases.validate_attribute_value(attribute_id, value)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate attribute value: {str(e)}"
        )


@router.get(
    "/stats/overview",
    response_model=AttributeStatsDTO,
    summary="Get attribute statistics",
    description="Get overview statistics for attributes"
)
async def get_attribute_stats(
    use_cases: AttributeUseCases = Depends(get_attribute_use_cases)
) -> AttributeStatsDTO:
    """Get attribute statistics"""
    try:
        return await use_cases.get_attribute_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attribute statistics: {str(e)}"
        )


# Category-Attribute relationship endpoints

@router.post(
    "/categories/{category_id}/assign",
    response_model=List[CategoryAttributeDTO],
    summary="Assign attributes to category",
    description="Assign one or more attributes to a category"
)
async def assign_attributes_to_category(
    category_id: UUID,
    assignment_data: CategoryAttributeCreateDTO,
    use_cases: AttributeUseCases = Depends(get_attribute_use_cases)
) -> List[CategoryAttributeDTO]:
    """Assign attributes to a category"""
    try:
        return await use_cases.assign_attributes_to_category(category_id, assignment_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign attributes to category: {str(e)}"
        )


@router.get(
    "/categories/{category_id}",
    response_model=List[AttributeResponseDTO],
    summary="Get category attributes",
    description="Get all attributes assigned to a specific category"
)
async def get_category_attributes(
    category_id: UUID,
    use_cases: AttributeUseCases = Depends(get_attribute_use_cases)
) -> List[AttributeResponseDTO]:
    """Get attributes assigned to a category"""
    try:
        return await use_cases.get_category_attributes(category_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get category attributes: {str(e)}"
        )