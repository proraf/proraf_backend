from typing import Optional, List, TypeVar, Generic
from pydantic import BaseModel, Field

T = TypeVar('T')

class Pagination(BaseModel):
    total: int = Field(..., example=100)
    page: int = Field(..., example=1)
    page_size: int = Field(..., example=10)
    has_next: bool = Field(..., example=True)
    has_prev: bool = Field(..., example=False)

class PaginatedResponse(BaseModel, Generic[T]):
    total: int = Field(..., example=100)
    items: List[T] = Field(..., example=[])