from abc import ABC, abstractmethod

from api.v1.schemas.item_schema import ItemCreateSchema
from models.item_model import ItemModel
from repositories import TSession


class IASyncItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, session: TSession, item_id: str) -> ItemModel | None: ...

    @abstractmethod
    async def create(self, session: TSession, item: ItemCreateSchema) -> ItemModel: ...

    @abstractmethod
    async def list(self, session: TSession) -> list[ItemModel]: ...

    @abstractmethod
    async def update(self, session: TSession, item_id: str, update_data: ItemCreateSchema) -> ItemModel | None: ...

    @abstractmethod
    async def delete(self, session: TSession, item_id: str) -> bool: ...
