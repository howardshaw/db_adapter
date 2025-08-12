import logging
from typing import List

from asgiref.sync import sync_to_async
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from api.v1.schemas.item_schema import ItemCreateSchema
from infras.executors import thread_pool
from models.item_model import ItemModel
from ports.async_session_execution import IAsyncExecutionStrategy
from repositories.item_async_repository import IASyncItemRepository
from .async_session import AsyncSession as InfraAsyncSession
from .item_po import ItemPO
from .sync_session import SyncSession as InfraSyncSession

logger = logging.getLogger(__name__)


class ItemRepository:
    async def _list(self, session: AsyncSession) -> list[ItemModel]:
        stmt = select(ItemPO)
        result = await session.execute(stmt)
        items = result.scalars().all()
        if not items:
            return []
        return [ItemModel.model_validate(i) for i in items]

    def _list_sync(self, session: Session) -> List[ItemModel]:
        stmt = select(ItemPO)
        result = session.execute(stmt)
        items = result.scalars().all()
        return [ItemModel.model_validate(i) for i in items]


class AsyncItemRepository(IASyncItemRepository):
    def __init__(self):
        super().__init__()
        logger.info("init async item repository")

    async def get_by_id(self, session: InfraAsyncSession, item_id: int) -> ItemModel | None:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = await session.execute(stmt)
        item = result.scalar_one_or_none()
        return ItemModel.model_validate(item) if item else None

    async def create(self, session: InfraAsyncSession, item: ItemCreateSchema) -> ItemModel:
        item_po = ItemPO(
            name=item.name,
            description=item.description,
            quantity=item.quantity,
            price=item.price,
        )
        session.add(item_po)
        await session.flush()
        await session.refresh(item_po)
        return ItemModel.model_validate(item_po)

    async def list(self, session: InfraAsyncSession) -> list[ItemModel]:
        stmt = select(ItemPO)
        result = await session.execute(stmt)
        items = result.scalars().all()
        if not items:
            return []
        return [ItemModel.model_validate(i) for i in items]

    async def update(self, session: InfraAsyncSession, item_id: str, update_data: ItemCreateSchema) -> ItemModel | None:
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

    async def delete(self, session: InfraAsyncSession, item_id: str) -> bool:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = await session.execute(stmt)
        item = result.scalar_one_or_none()
        if not item:
            return False

        await session.delete(item)
        await session.flush()
        return True


class SyncToAsyncItemRepository(IASyncItemRepository):
    def __init__(self):
        super().__init__()
        logger.info("init sync to async item repository")

    async def get_by_id(self, session: InfraSyncSession, item_id: int) -> ItemModel | None:
        return await sync_to_async(self._get_by_id, thread_sensitive=False, executor=thread_pool)(session, item_id)

    def _get_by_id(self, session: Session, item_id: int) -> ItemModel | None:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = session.execute(stmt)
        item = result.scalar_one_or_none()
        return ItemModel.model_validate(item) if item else None

    async def create(self, session: InfraSyncSession, item: ItemCreateSchema) -> ItemModel:
        return await sync_to_async(self._create, thread_sensitive=False, executor=thread_pool)(session, item)

    def _create(self, session: Session, item: ItemCreateSchema) -> ItemModel:
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

    async def list(self, session: InfraSyncSession) -> list[ItemModel]:
        return await sync_to_async(self._list, thread_sensitive=False, executor=thread_pool)(session)

    def _list(self, session: Session) -> List[ItemModel]:
        stmt = select(ItemPO)
        result = session.execute(stmt)
        items = result.scalars().all()
        return [ItemModel.model_validate(i) for i in items]

    async def update(self, session: InfraSyncSession, item_id: int, update_data: ItemCreateSchema) -> ItemModel | None:
        return await sync_to_async(self._update, thread_sensitive=False, executor=thread_pool)(session, item_id,
                                                                                               update_data)

    def _update(self, session: Session, item_id: int, update_data: ItemCreateSchema) -> ItemModel | None:
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

    async def delete(self, session: InfraSyncSession, item_id: int) -> bool:
        return await sync_to_async(self._delete, thread_sensitive=False, executor=thread_pool)(session, item_id)

    def _delete(self, session: Session, item_id: int) -> bool:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = session.execute(stmt)
        item = result.scalar_one_or_none()
        if not item:
            return False

        session.delete(item)
        session.flush()
        return True


class UniformAsyncItemRepository(IASyncItemRepository):
    def __init__(self, strategy: IAsyncExecutionStrategy):
        super().__init__()
        self.strategy = strategy
        logger.info(f"init UniformItemRepository using strategy {type(strategy)} ")

    async def get_by_id(self, session: InfraAsyncSession | InfraSyncSession, item_id: int) -> ItemModel | None:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = await self.strategy.execute(session, stmt)
        item = result.scalar_one_or_none()
        return ItemModel.model_validate(item) if item else None

    async def list(self, session: InfraAsyncSession | InfraSyncSession) -> list[ItemModel]:
        stmt = select(ItemPO)
        result = await self.strategy.execute(session, stmt)
        items = result.scalars().all()
        return [ItemModel.model_validate(i) for i in items]

    async def create(self, session: InfraAsyncSession | InfraSyncSession, item: ItemCreateSchema) -> ItemModel:
        item_po = ItemPO(**item.model_dump())
        # add is now synchronous
        self.strategy.add(session, item_po)
        await self.strategy.flush(session)
        await self.strategy.refresh(session, item_po)
        return ItemModel.model_validate(item_po)

    async def update(self, session: InfraAsyncSession | InfraSyncSession, item_id: int,
                     update_data: ItemCreateSchema) -> ItemModel | None:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = await self.strategy.execute(session, stmt)
        item = result.scalar_one_or_none()
        if not item:
            return None
        for field, value in update_data.model_dump().items():
            setattr(item, field, value)
        await self.strategy.flush(session)
        await self.strategy.refresh(session, item)
        return ItemModel.model_validate(item)

    async def delete(self, session: InfraAsyncSession | InfraSyncSession, item_id: int) -> bool:
        stmt = select(ItemPO).where(ItemPO.id == item_id)
        result = await self.strategy.execute(session, stmt)
        item = result.scalar_one_or_none()
        if not item:
            return False
        await self.strategy.delete(session, item)
        await self.strategy.flush(session)
        return True
