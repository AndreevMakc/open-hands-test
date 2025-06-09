from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EntityId(BaseModel):
    """Base value object for entity identifiers"""
    value: UUID = Field(default_factory=uuid4)
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __hash__(self) -> int:
        return hash(self.value)


class Timestamps(BaseModel):
    """Value object for entity timestamps"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    def mark_updated(self) -> "Timestamps":
        """Mark entity as updated"""
        return self.model_copy(update={"updated_at": datetime.utcnow()})


class Money(BaseModel):
    """Value object for monetary amounts"""
    amount: float = Field(ge=0, description="Amount in base currency units")
    currency: str = Field(default="RUB", description="Currency code")
    
    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


class SEOData(BaseModel):
    """Value object for SEO metadata"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    keywords: list[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            list: lambda v: v if v else []
        }