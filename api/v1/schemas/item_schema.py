from pydantic import Field, BaseModel

from .base_schema import BaseSchema


class ItemSchema(BaseSchema):
    name: str = Field(..., description="Item name")
    description: str | None = Field(None, description="Item description")
    quantity: int = Field(..., description="Item quantity", ge=0)
    price: float = Field(..., description="Item price", ge=0.0)


class ItemCreateSchema(BaseModel):
    name: str
    description: str | None = None
    quantity: int
    price: float
