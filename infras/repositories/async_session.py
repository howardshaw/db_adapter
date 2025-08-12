from sqlalchemy.ext.asyncio import AsyncSession as SQLAlchemyAsyncSession

from ports.async_session import IAsyncSession


class AsyncSession(SQLAlchemyAsyncSession, IAsyncSession):
    pass
