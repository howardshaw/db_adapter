from dependency_injector import containers, providers

from config import get_settings
from infras.repositories.async_session_execution import SyncToAsyncExecutionStrategy, AsyncExecutionStrategy
from infras.repositories.async_transaction import AsyncTransactionManager, SyncToAsyncTransactionManager
from infras.repositories.factory import sync_session_factory, async_session_factory, get_session_factory
from infras.repositories.item_async_repository import (
    AsyncItemRepository,
    SyncToAsyncItemRepository,
    UniformAsyncItemRepository
)
from infras.repositories.item_sync_repository import (
    SyncItemRepository,
    AsyncToSyncItemRepository,
    UniformSyncItemRepository,
)
from infras.repositories.sync_session_execution import AsyncToSyncExecutionStrategy, SyncExecutionStrategy
from infras.repositories.sync_transaction import SyncTransactionManager, AsyncToSyncTransactionManager
from services.item_async_service import AsyncItemService
from services.item_sync_service import SyncItemService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            'api.v1.controllers.item_async_controller',
            'api.v1.controllers.item_sync_controller',
        ]
    )
    config = providers.Configuration()

    settings = providers.Singleton(get_settings)

    sync_session_factory = providers.Factory(
        sync_session_factory,
        settings=settings,
    )
    async_session_factory = providers.Factory(
        async_session_factory,
        settings=settings,
    )
    session_factory = providers.Factory(
        get_session_factory,
        settings=settings,
    )
    # sync_transaction_manager = providers.Factory(
    #     SyncTransactionManager,
    #     session_factory=sync_session_factory.provided
    # )
    # async_transaction_manager = providers.Factory(
    #     AsyncTransactionManager,
    #     session_factory=async_session_factory.provided
    # )
    # async_to_sync_transaction_manager = providers.Factory(
    #     AsyncToSyncTransactionManager,
    #     async_transaction_manager=async_transaction_manager.provided
    # )
    #
    # sync_item_repository = providers.Factory(
    #     SyncItemRepository
    # )
    # async_to_sync_item_repository = providers.Factory(
    #     AsyncToSyncItemRepository
    # )
    #
    # async_item_repository = providers.Factory(
    #     AsyncItemRepository
    # )
    # sync_to_async_item_repository = providers.Factory(
    #     SyncToAsyncItemRepository
    # )
    # uniform_async_item_repository = providers.Factory(
    #     UniformAsyncItemRepository,
    #     strategy=providers.Factory(
    #         SyncToAsyncExecutionStrategy,
    #     ),
    # )

    sync_item_service = providers.Selector(
        settings.provided.REPO_DRIVER,
        async_db=providers.Factory(
            SyncItemService,
            transaction=providers.Factory(
                AsyncToSyncTransactionManager,
                async_transaction_manager=providers.Factory(
                    AsyncTransactionManager,
                    session_factory=async_session_factory
                )
            ),
            repo=providers.Factory(
                AsyncToSyncItemRepository
            ),
        ),
        sync_db=providers.Factory(
            SyncItemService,
            transaction=providers.Factory(
                SyncTransactionManager,
                session_factory=sync_session_factory
            ),
            repo=providers.Factory(
                SyncItemRepository
            ),
        ),
        uniform_async_db=providers.Factory(
            SyncItemService,
            transaction=providers.Factory(
                AsyncToSyncTransactionManager,
                async_transaction_manager=providers.Factory(
                    AsyncTransactionManager,
                    session_factory=async_session_factory
                )
            ),
            repo=providers.Factory(
                UniformSyncItemRepository,
                strategy=providers.Factory(
                    AsyncToSyncExecutionStrategy,
                ),
            ),
        ),
        uniform_sync_db=providers.Factory(
            SyncItemService,
            transaction=providers.Factory(
                SyncTransactionManager,
                session_factory=sync_session_factory
            ),
            repo=providers.Factory(
                UniformSyncItemRepository,
                strategy=providers.Factory(
                    SyncExecutionStrategy,
                ),
            ),
        )
    )

    async_item_service = providers.Selector(
        settings.provided.REPO_DRIVER,
        async_db=providers.Factory(
            AsyncItemService,
            transaction=providers.Factory(
                AsyncTransactionManager,
                session_factory=async_session_factory
            ),
            repo=providers.Factory(
                AsyncItemRepository
            ),
        ),
        sync_db=providers.Factory(
            AsyncItemService,
            transaction=providers.Factory(
                SyncToAsyncTransactionManager,
                sync_transaction_manager=providers.Factory(
                    SyncTransactionManager,
                    session_factory=sync_session_factory
                )
            ),
            repo=providers.Factory(
                SyncToAsyncItemRepository
            ),
        ),
        uniform_async_db=providers.Factory(
            AsyncItemService,
            transaction=providers.Factory(
                AsyncTransactionManager,
                session_factory=async_session_factory
            ),
            repo=providers.Factory(
                UniformAsyncItemRepository,
                strategy=providers.Factory(
                    AsyncExecutionStrategy,
                ),
            ),
        ),
        uniform_sync_db=providers.Factory(
            AsyncItemService,
            transaction=providers.Factory(
                SyncToAsyncTransactionManager,
                sync_transaction_manager=providers.Factory(
                    SyncTransactionManager,
                    session_factory=sync_session_factory
                )
            ),
            repo=providers.Factory(
                UniformAsyncItemRepository,
                strategy=providers.Factory(
                    SyncToAsyncExecutionStrategy,
                ),
            ),
        )
    )
