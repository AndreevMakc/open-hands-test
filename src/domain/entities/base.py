from abc import ABC
from typing import Optional
from pydantic import BaseModel

from ..value_objects.common import EntityId, Timestamps


class BaseEntity(BaseModel, ABC):
    """Base entity class"""
    id: EntityId
    timestamps: Timestamps
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def mark_updated(self) -> "BaseEntity":
        """Mark entity as updated"""
        return self.model_copy(update={"timestamps": self.timestamps.mark_updated()})
    
    class Config:
        arbitrary_types_allowed = True