"""Tests for service layer."""

import pytest

from api.v1.schemas.item_schema import ItemCreateSchema
from models.item_model import ItemModel
from services.item_async_service import AsyncItemService
from services.item_sync_service import SyncItemService


class TestAsyncItemService:
    """Test cases for AsyncItemService."""

    @pytest.mark.async_test
    @pytest.mark.unit
    async def test_list_items_empty(self, mock_async_service):
        """Test listing items when repository is empty."""
        mock_async_service.list.return_value = []

        service = AsyncItemService(
            transaction=mock_async_service,
            repo=mock_async_service
        )

        result = await service.list()
        assert result == []
        mock_async_service.list.assert_called_once()

    @pytest.mark.async_test
    @pytest.mark.unit
    async def test_list_items_with_data(self, mock_async_service):
        """Test listing items with data."""
        mock_items = [
            ItemModel(id="1", name="Item 1", description="Desc 1", price=10.0, category="test"),
            ItemModel(id="2", name="Item 2", description="Desc 2", price=20.0, category="test")
        ]
        mock_async_service.list.return_value = mock_items

        service = AsyncItemService(
            transaction=mock_async_service,
            repo=mock_async_service
        )

        result = await service.list()
        assert len(result) == 2
        assert result[0].name == "Item 1"
        assert result[1].name == "Item 2"

    @pytest.mark.async_test
    @pytest.mark.unit
    async def test_get_item_found(self, mock_async_service):
        """Test getting an existing item."""
        mock_item = ItemModel(id="1", name="Test Item", description="Test Desc", price=99.99, category="test")
        mock_async_service.get.return_value = mock_item

        service = AsyncItemService(
            transaction=mock_async_service,
            repo=mock_async_service
        )

        result = await service.get("1")
        assert result == mock_item
        mock_async_service.get.assert_called_once_with("1")

    @pytest.mark.async_test
    @pytest.mark.unit
    async def test_get_item_not_found(self, mock_async_service):
        """Test getting a non-existent item."""
        mock_async_service.get.return_value = None

        service = AsyncItemService(
            transaction=mock_async_service,
            repo=mock_async_service
        )

        result = await service.get("non-existent")
        assert result is None

    @pytest.mark.async_test
    @pytest.mark.unit
    async def test_create_item_success(self, mock_async_service):
        """Test creating a new item."""
        item_data = ItemCreateSchema(
            name="New Item",
            description="New description",
            price=50.0,
            category="electronics"
        )
        mock_item = ItemModel(
            id="new-id",
            name=item_data.name,
            description=item_data.description,
            price=item_data.price,
            category=item_data.category
        )
        mock_async_service.create.return_value = mock_item

        service = AsyncItemService(
            transaction=mock_async_service,
            repo=mock_async_service
        )

        result = await service.create(item_data)
        assert result == mock_item
        mock_async_service.create.assert_called_once_with(item_data)

    @pytest.mark.async_test
    @pytest.mark.unit
    async def test_update_item_success(self, mock_async_service):
        """Test updating an existing item."""
        item_data = ItemCreateSchema(
            name="Updated Item",
            description="Updated description",
            price=75.0,
            category="books"
        )
        mock_item = ItemModel(
            id="1",
            name=item_data.name,
            description=item_data.description,
            price=item_data.price,
            category=item_data.category
        )
        mock_async_service.update.return_value = mock_item

        service = AsyncItemService(
            transaction=mock_async_service,
            repo=mock_async_service
        )

        result = await service.update("1", item_data)
        assert result == mock_item
        mock_async_service.update.assert_called_once_with("1", item_data)

    @pytest.mark.async_test
    @pytest.mark.unit
    async def test_update_item_not_found(self, mock_async_service):
        """Test updating a non-existent item."""
        item_data = ItemCreateSchema(
            name="Updated Item",
            description="Updated description",
            price=75.0,
            category="books"
        )
        mock_async_service.update.return_value = None

        service = AsyncItemService(
            transaction=mock_async_service,
            repo=mock_async_service
        )

        result = await service.update("non-existent", item_data)
        assert result is None

    @pytest.mark.async_test
    @pytest.mark.unit
    async def test_delete_item_success(self, mock_async_service):
        """Test deleting an existing item."""
        mock_async_service.delete.return_value = True

        service = AsyncItemService(
            transaction=mock_async_service,
            repo=mock_async_service
        )

        result = await service.delete("1")
        assert result is True
        mock_async_service.delete.assert_called_once_with("1")

    @pytest.mark.async_test
    @pytest.mark.unit
    async def test_delete_item_not_found(self, mock_async_service):
        """Test deleting a non-existent item."""
        mock_async_service.delete.return_value = False

        service = AsyncItemService(
            transaction=mock_async_service,
            repo=mock_async_service
        )

        result = await service.delete("non-existent")
        assert result is False


class TestSyncItemService:
    """Test cases for SyncItemService."""

    @pytest.mark.unit
    def test_list_items_empty(self, mock_sync_service):
        """Test listing items when repository is empty."""
        mock_sync_service.list.return_value = []

        service = SyncItemService(
            transaction=mock_sync_service,
            repo=mock_sync_service
        )

        result = service.list()
        assert result == []
        mock_sync_service.list.assert_called_once()

    @pytest.mark.unit
    def test_list_items_with_data(self, mock_sync_service):
        """Test listing items with data."""
        mock_items = [
            ItemModel(id="1", name="Item 1", description="Desc 1", price=10.0, category="test"),
            ItemModel(id="2", name="Item 2", description="Desc 2", price=20.0, category="test")
        ]
        mock_sync_service.list.return_value = mock_items

        service = SyncItemService(
            transaction=mock_sync_service,
            repo=mock_sync_service
        )

        result = service.list()
        assert len(result) == 2
        assert result[0].name == "Item 1"
        assert result[1].name == "Item 2"

    @pytest.mark.unit
    def test_get_item_found(self, mock_sync_service):
        """Test getting an existing item."""
        mock_item = ItemModel(id="1", name="Test Item", description="Test Desc", price=99.99, category="test")
        mock_sync_service.get.return_value = mock_item

        service = SyncItemService(
            transaction=mock_sync_service,
            repo=mock_sync_service
        )

        result = service.get("1")
        assert result == mock_item
        mock_sync_service.get.assert_called_once_with("1")

    @pytest.mark.unit
    def test_get_item_not_found(self, mock_sync_service):
        """Test getting a non-existent item."""
        mock_sync_service.get.return_value = None

        service = SyncItemService(
            transaction=mock_sync_service,
            repo=mock_sync_service
        )

        result = service.get("non-existent")
        assert result is None

    @pytest.mark.unit
    def test_create_item_success(self, mock_sync_service):
        """Test creating a new item."""
        item_data = ItemCreateSchema(
            name="New Item",
            description="New description",
            price=50.0,
            category="electronics"
        )
        mock_item = ItemModel(
            id="new-id",
            name=item_data.name,
            description=item_data.description,
            price=item_data.price,
            category=item_data.category
        )
        mock_sync_service.create.return_value = mock_item

        service = SyncItemService(
            transaction=mock_sync_service,
            repo=mock_sync_service
        )

        result = service.create(item_data)
        assert result == mock_item
        mock_sync_service.create.assert_called_once_with(item_data)

    @pytest.mark.unit
    def test_update_item_success(self, mock_sync_service):
        """Test updating an existing item."""
        item_data = ItemCreateSchema(
            name="Updated Item",
            description="Updated description",
            price=75.0,
            category="books"
        )
        mock_item = ItemModel(
            id="1",
            name=item_data.name,
            description=item_data.description,
            price=item_data.price,
            category=item_data.category
        )
        mock_sync_service.update.return_value = mock_item

        service = SyncItemService(
            transaction=mock_sync_service,
            repo=mock_sync_service
        )

        result = service.update("1", item_data)
        assert result == mock_item
        mock_sync_service.update.assert_called_once_with("1", item_data)

    @pytest.mark.unit
    def test_delete_item_success(self, mock_sync_service):
        """Test deleting an existing item."""
        mock_sync_service.delete.return_value = True

        service = SyncItemService(
            transaction=mock_sync_service,
            repo=mock_sync_service
        )

        result = service.delete("1")
        assert result is True
        mock_sync_service.delete.assert_called_once_with("1")
