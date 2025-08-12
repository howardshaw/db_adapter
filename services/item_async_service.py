import logging
from typing import Sequence

from api.v1.schemas.item_schema import ItemCreateSchema
from models.item_model import ItemModel
from ports.async_transaction import IAsyncTransactionManager
from repositories import TSession
from repositories.item_async_repository import IASyncItemRepository


class AsyncItemService:
    def __init__(self, transaction: IAsyncTransactionManager, repo: IASyncItemRepository):
        self.transaction = transaction
        self.repo = repo
        self.logger = logging.getLogger(__name__)
        self.logger.info("init async item service")

    async def get(self, item_id: str) -> ItemModel | None:
        """Get item by ID using session"""
        return await self.transaction.transactional(read_only=True)(self._get)(item_id)

    async def create(self, item: ItemCreateSchema) -> ItemModel:
        """Create new item using transaction"""
        return await self.transaction.transactional(read_only=False)(self._create)(item)

    async def list(self) -> Sequence[ItemModel]:
        """List all items using session"""
        return await self.transaction.transactional(read_only=True)(self._list)()

    async def update(self, item_id: str, item: ItemCreateSchema) -> ItemModel | None:
        """Update item using transaction"""
        return await self.transaction.transactional(read_only=False)(self._update)(item_id, item)

    async def delete(self, item_id: str) -> bool:
        """Delete item using transaction"""
        return await self.transaction.transactional(read_only=False)(self._delete)(item_id)

    # Internal methods designed to work with transactional decorator
    async def _get(self, session: TSession, item_id: str) -> ItemModel | None:
        """Get item by ID - designed for transactional decorator"""
        return await self.repo.get_by_id(session, item_id)

    async def _create(self, session: TSession, item: ItemCreateSchema) -> ItemModel:
        """Create new item - designed for transactional decorator"""
        return await self.repo.create(session, item)

    async def _list(self, session: TSession) -> Sequence[ItemModel]:
        """List all items - designed for transactional decorator"""
        return await self.repo.list(session)

    async def _update(self, session, item_id: str, item: ItemCreateSchema) -> ItemModel | None:
        """Update item - designed for transactional decorator"""
        return await self.repo.update(session, item_id, item)

    async def _delete(self, session, item_id: str) -> bool:
        """Delete item - designed for transactional decorator"""
        return await self.repo.delete(session, item_id)

    # Alternative approach using execute_with_* methods directly
    async def get_with_execute(self, item_id: str) -> ItemModel | None:
        """Get item by ID using execute_with_session"""

        async def _get_by_id(session: TSession):
            return await self.repo.get_by_id(session, item_id)

        return await self.transaction.execute_with_session(_get_by_id)

    async def create_with_execute(self, item: ItemCreateSchema) -> ItemModel:
        """Create new item using execute_with_transaction"""

        async def _create(session: TSession):
            return await self.repo.create(session, item)

        return await self.transaction.execute_with_transaction(_create)

    async def list_with_execute(self) -> Sequence[ItemModel]:
        """List all items using execute_with_session"""

        async def _list(session: TSession):
            return await self.repo.list(session)

        return await self.transaction.execute_with_session(_list)

    async def update_with_execute(self, item_id: str, item: ItemCreateSchema) -> ItemModel | None:
        """Update item using execute_with_transaction"""

        async def _update(session: TSession):
            return await self.repo.update(session, item_id, item)

        return await self.transaction.execute_with_transaction(_update)

    async def delete_with_execute(self, item_id: str) -> bool:
        """Delete item using execute_with_transaction"""

        async def _delete(session: TSession):
            return await self.repo.delete(session, item_id)

        return await self.transaction.execute_with_transaction(_delete)

