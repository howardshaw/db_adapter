from sqlalchemy.orm import Session as SQLAlchemySession

from ports.sync_session import ISyncSession


class SyncSession(SQLAlchemySession, ISyncSession):
    pass
