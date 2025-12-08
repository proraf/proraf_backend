from typing import Optional, List, TypeVar, Generic
from pydantic import BaseModel, Field

T = TypeVar('T')

class Pagination(BaseModel):
    total: int = Field(..., json_schema_extra={"example": 100})
    page: int = Field(..., json_schema_extra={"example": 1})
    page_size: int = Field(..., json_schema_extra={"example": 10})
    has_next: bool = Field(..., json_schema_extra={"example": True})
    has_prev: bool = Field(..., json_schema_extra={"example": False})

class PaginatedResponse(BaseModel, Generic[T]):
    total: int = Field(..., json_schema_extra={"example": 100})
    items: List[T] = Field(..., json_schema_extra={"example": []})