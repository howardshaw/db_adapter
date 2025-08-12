import logging
from typing import List

from asgiref.sync import async_to_sync
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.item_schema import ItemCreateSchema
from models.item_model import ItemModel
from ports.sync_session_execution import ISyncExecutionStrategy
from repositories.item_sync_repository import ISyncItemRepository
from .async_session import AsyncSession as InfraAsyncSession
from .item_po import ItemPO
from .sync_session import SyncSession as InfraSyncSession

logger = logging.getLogger(__name__)


class SyncItemRepository(ISyncItemRepository):
    def __init__(self):
        super().__init__()
        logger.error("init sync item repository")

    def get_by_id(self, session: InfraSyncSession, item_id: str) -> ItemModel | None:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = session.execute(stmt)
        item = result.scalar_one_or_none()
        return ItemModel.model_validate(item) if item else None

    def create(self, session: InfraSyncSession, item: ItemCreateSchema) -> ItemModel:
        item_po = ItemPO(
            name=item.name,
            description=item.description,
            quantity=item.quantity,
            price=item.price,
        )
        session.add(item_po)
        session.flush()
        session.refresh(item_po)
        return ItemModel.model_validate(item_po)

    def list(self, session: InfraSyncSession) -> list[ItemModel]:
        stmt = select(ItemPO)
        result = session.execute(stmt)
        items = result.scalars().all()
        return [ItemModel.model_validate(i) for i in items]

    def update(self, session: InfraSyncSession, item_id: str, update_data: ItemCreateSchema) -> ItemModel | None:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = session.execute(stmt)
        item = result.scalar_one_or_none()
        if not item:
            return None

        for field, value in update_data.model_dump().items():
            setattr(item, field, value)

        session.flush()
        session.refresh(item)
        return ItemModel.model_validate(item)

    def delete(self, session: InfraSyncSession, item_id: str) -> bool:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = session.execute(stmt)
        item = result.scalar_one_or_none()
        if not item:
            return False

        session.delete(item)
        session.flush()
        return True


class AsyncToSyncItemRepository(ISyncItemRepository):
    def __init__(self):
        super().__init__()
        logger.error("init async to sync item repository")

    def get_by_id(self, session: InfraAsyncSession, item_id: str) -> ItemModel | None:
        return async_to_sync(self._get_by_id)(session, item_id)

    async def _get_by_id(self, session: AsyncSession, item_id: str) -> ItemModel | None:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = await session.execute(stmt)
        item = result.scalar_one_or_none()
        return ItemModel.model_validate(item) if item else None

    def create(self, session: InfraAsyncSession, item: ItemCreateSchema) -> ItemModel:
        return async_to_sync(self._create)(session, item)

    async def _create(self, session: AsyncSession, item: ItemCreateSchema) -> ItemModel:
        item_po = ItemPO(**item.model_dump())
        session.add(item_po)
        await session.flush()
        await session.refresh(item_po)
        return ItemModel.model_validate(item_po)

    def list(self, session: InfraAsyncSession) -> list[ItemModel]:
        return async_to_sync(self._list)(session)

    async def _list(self, session: AsyncSession) -> List[ItemModel]:
        stmt = select(ItemPO)
        result = await session.execute(stmt)
        items = result.scalars().all()
        return [ItemModel.model_validate(i) for i in items]

    def update(self, session: InfraAsyncSession, item_id: str, update_data: ItemCreateSchema) -> ItemModel | None:
        return async_to_sync(self._update)(session, item_id, update_data)

    async def _update(self, session: AsyncSession, item_id: str, update_data: ItemCreateSchema) -> ItemModel | None:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = await session.execute(stmt)
        item = result.scalar_one_or_none()
        if not item:
            return None
        for field, value in update_data.model_dump().items():
            setattr(item, field, value)
        await session.flush()
        await session.refresh(item)
        return ItemModel.model_validate(item)

    def delete(self, session: InfraAsyncSession, item_id: str) -> bool:
        return async_to_sync(self._delete)(session, item_id)

    async def _delete(self, session: AsyncSession, item_id: str) -> bool:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = await session.execute(stmt)
        item = result.scalar_one_or_none()
        if not item:
            return False
        await session.delete(item)
        await session.flush()
        return True


class UniformSyncItemRepository(ISyncItemRepository):
    def __init__(self, strategy: ISyncExecutionStrategy):
        super().__init__()
        self.strategy = strategy
        logger.info(f"init UniformSyncItemRepository using strategy {type(strategy)} ")

    def get_by_id(self, session: InfraAsyncSession | InfraSyncSession, item_id: str) -> ItemModel | None:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = self.strategy.execute(session, stmt)
        item = result.scalar_one_or_none()
        return ItemModel.model_validate(item) if item else None

    def list(self, session: InfraAsyncSession | InfraSyncSession) -> list[ItemModel]:
        stmt = select(ItemPO)
        result = self.strategy.execute(session, stmt)
        items = result.scalars().all()
        return [ItemModel.model_validate(i) for i in items]

    def create(self, session: InfraAsyncSession | InfraSyncSession, item: ItemCreateSchema) -> ItemModel:
        item_po = ItemPO(**item.model_dump())
        self.strategy.add(session, item_po)
        self.strategy.flush(session)
        self.strategy.refresh(session, item_po)
        return ItemModel.model_validate(item_po)

    def update(self, session: InfraAsyncSession | InfraSyncSession, item_id: str,
               update_data: ItemCreateSchema) -> ItemModel | None:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = self.strategy.execute(session, stmt)
        item = result.scalar_one_or_none()
        if not item:
            return None
        for field, value in update_data.model_dump().items():
            setattr(item, field, value)
        self.strategy.flush(session)
        self.strategy.refresh(session, item)
        return ItemModel.model_validate(item)

    def delete(self, session: InfraAsyncSession | InfraSyncSession, item_id: str) -> bool:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = self.strategy.execute(session, stmt)
        item = result.scalar_one_or_none()
        if not item:
            return False
        self.strategy.delete(session, item)
        self.strategy.flush(session)
        return True
