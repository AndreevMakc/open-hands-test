from enum import Enum
from typing import Any, Optional, Union
from pydantic import BaseModel, Field, validator


class AttributeType(str, Enum):
    """Attribute type enumeration"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    LIST = "list"
    DATE = "date"


class ValidationRule(BaseModel):
    """Base validation rule"""
    pass


class StringValidation(ValidationRule):
    """String validation rules"""
    min_length: Optional[int] = Field(None, ge=0)
    max_length: Optional[int] = Field(None, ge=0)
    pattern: Optional[str] = None


class NumberValidation(ValidationRule):
    """Number validation rules"""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    decimal_places: Optional[int] = Field(None, ge=0)


class ListValidation(ValidationRule):
    """List validation rules"""
    allowed_values: list[str] = Field(default_factory=list)
    multiple_selection: bool = Field(default=False)


class AttributeOptions(BaseModel):
    """Attribute configuration options"""
    validation: Optional[Union[StringValidation, NumberValidation, ListValidation]] = None
    default_value: Optional[Any] = None
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    
    @validator('validation', pre=True)
    def validate_validation_rules(cls, v, values):
        """Validate validation rules based on attribute type"""
        if v is None:
            return v
        
        # This would be validated in the entity based on attribute type
        return v


class AttributeValue(BaseModel):
    """Value object for attribute values"""
    value: Any
    attribute_type: AttributeType
    
    @validator('value')
    def validate_value_type(cls, v, values):
        """Validate value matches attribute type"""
        attr_type = values.get('attribute_type')
        
        if attr_type == AttributeType.STRING and not isinstance(v, str):
            raise ValueError("String attribute must have string value")
        elif attr_type == AttributeType.NUMBER and not isinstance(v, (int, float)):
            raise ValueError("Number attribute must have numeric value")
        elif attr_type == AttributeType.BOOLEAN and not isinstance(v, bool):
            raise ValueError("Boolean attribute must have boolean value")
        elif attr_type == AttributeType.LIST and not isinstance(v, list):
            raise ValueError("List attribute must have list value")
        elif attr_type == AttributeType.DATE and not isinstance(v, str):
            # Date should be ISO format string
            raise ValueError("Date attribute must have ISO date string value")
        
        return v
    
    def __str__(self) -> str:
        return str(self.value)