from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int= Field(ge=1)
    pages: int = Field(ge=0)


class Message(BaseModel):
    message: str = Field(min_length=1, max_lengh=500)
