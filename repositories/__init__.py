from typing import TypeVar, ParamSpec

from ports.async_session import IAsyncSession
from ports.sync_session import ISyncSession

# Type variables for session types
SyncS = TypeVar('SyncS', bound=ISyncSession)
AsyncS = TypeVar('AsyncS', bound=IAsyncSession)
TSession = TypeVar('TSession', bound=ISyncSession | IAsyncSession)

# Generic type variable for operation results
T = TypeVar('T')
P = ParamSpec("P")
