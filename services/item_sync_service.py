import logging
from typing import Sequence

from api.v1.schemas.item_schema import ItemCreateSchema
from models.item_model import ItemModel
from ports.sync_transaction import ISyncTransactionManager
from repositories.item_sync_repository import ISyncItemRepository
from repositories import TSession

class SyncItemService:
    def __init__(self, transaction: ISyncTransactionManager, repo: ISyncItemRepository):
        self.transaction = transaction
        self.repo = repo
        self.logger = logging.getLogger(__name__)
        self.logger.info("init sync item service")

    def get(self, item_id: str) -> ItemModel | None:
        """Get item by ID using session"""
        return self.transaction.transactional(read_only=True)(self._get)(item_id)

    def create(self, item: ItemCreateSchema) -> ItemModel:
        """Create new item using transaction"""
        return self.transaction.transactional(read_only=False)(self._create)(item)

    def list(self) -> Sequence[ItemModel]:
        """List all items using session"""
        return self.transaction.transactional(read_only=True)(self._list)()

    def update(self, item_id: str, item: ItemCreateSchema) -> ItemModel | None:
        """Update item using transaction"""
        return self.transaction.transactional(read_only=False)(self._update)(item_id, item)

    def delete(self, item_id: str) -> bool:
        """Delete item using transaction"""
        return self.transaction.transactional(read_only=False)(self._delete)(item_id)

    # Internal methods designed to work with transactional decorator
    def _get(self, session: TSession, item_id: str) -> ItemModel | None:
        """Get item by ID - designed for transactional decorator"""
        return self.repo.get_by_id(session, item_id)

    def _create(self, session: TSession, item: ItemCreateSchema) -> ItemModel:
        """Create new item - designed for transactional decorator"""
        return self.repo.create(session, item)

    def _list(self, session: TSession) -> Sequence[ItemModel]:
        """List all items - designed for transactional decorator"""
        return self.repo.list(session)

    def _update(self, session: TSession, item_id: str, item: ItemCreateSchema) -> ItemModel | None:
        """Update item - designed for transactional decorator"""
        return self.repo.update(session, item_id, item)

    def _delete(self, session: TSession, item_id: str) -> bool:
        """Delete item - designed for transactional decorator"""
        return self.repo.delete(session, item_id)

    # Alternative approach using execute_with_* methods directly
    def get_with_execute(self, item_id: str) -> ItemModel | None:
        """Get item by ID using execute_with_session"""
        def _get_by_id(session: TSession):
            return self.repo.get_by_id(session, item_id)
        
        return self.transaction.execute_with_session(_get_by_id)

    def create_with_execute(self, item: ItemCreateSchema) -> ItemModel:
        """Create new item using execute_with_transaction"""
        def _create(session: TSession):
            return self.repo.create(session, item)
        
        return self.transaction.execute_with_transaction(_create)

    def list_with_execute(self) -> Sequence[ItemModel]:
        """List all items using execute_with_session"""
        def _list(session: TSession):
            return self.repo.list(session)
        
        return self.transaction.execute_with_session(_list)

    def update_with_execute(self, item_id: str, item: ItemCreateSchema) -> ItemModel | None:
        """Update item using execute_with_transaction"""
        def _update(session: TSession):
            return self.repo.update(session, item_id, item)
        
        return self.transaction.execute_with_transaction(_update)

    def delete_with_execute(self, item_id: str) -> bool:
        """Delete item using execute_with_transaction"""
        def _delete(session: TSession):
            return self.repo.delete(session, item_id)
        
        return self.transaction.execute_with_transaction(_delete)
