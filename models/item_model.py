from .base_model import BaseModel


class ItemModel(BaseModel):
    name: str
    description: str
    quantity: int
    price: float
