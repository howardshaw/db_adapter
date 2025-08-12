"""Tests for domain models."""

from datetime import datetime

import pytest

from models.item_model import ItemModel


class TestItemModel:
    """Test cases for ItemModel."""

    def test_item_model_creation(self):
        """Test creating an ItemModel instance."""
        item = ItemModel(
            id="test-id",
            name="Test Item",
            description="Test description",
            price=99.99,
            category="test"
        )

        assert item.id == "test-id"
        assert item.name == "Test Item"
        assert item.description == "Test description"
        assert item.price == 99.99
        assert item.category == "test"
        assert isinstance(item.created_at, datetime)
        assert isinstance(item.updated_at, datetime)

    def test_item_model_defaults(self):
        """Test ItemModel with default values."""
        item = ItemModel(
            name="Test Item",
            description="Test description",
            price=99.99,
            category="test"
        )

        assert item.name == "Test Item"
        assert item.description == "Test description"
        assert item.price == 99.99
        assert item.category == "test"
        assert item.id is not None
        assert isinstance(item.created_at, datetime)
        assert isinstance(item.updated_at, datetime)

    def test_item_model_validation(self):
        """Test ItemModel validation."""
        # Test with valid data
        item = ItemModel(
            name="Valid Item",
            description="Valid description",
            price=0.01,
            category="valid"
        )
        assert item.name == "Valid Item"

        # Test price validation
        with pytest.raises(ValueError):
            ItemModel(
                name="Invalid Item",
                description="Invalid description",
                price=-1.0,
                category="invalid"
            )

    def test_item_model_to_dict(self):
        """Test converting ItemModel to dictionary."""
        item = ItemModel(
            id="test-id",
            name="Test Item",
            description="Test description",
            price=99.99,
            category="test"
        )

        item_dict = item.model_dump()

        assert item_dict["id"] == "test-id"
        assert item_dict["name"] == "Test Item"
        assert item_dict["description"] == "Test description"
        assert item_dict["price"] == 99.99
        assert item_dict["category"] == "test"
        assert "created_at" in item_dict
        assert "updated_at" in item_dict

    def test_item_model_from_dict(self):
        """Test creating ItemModel from dictionary."""
        item_data = {
            "id": "test-id",
            "name": "Test Item",
            "description": "Test description",
            "price": 99.99,
            "category": "test",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        item = ItemModel(**item_data)

        assert item.id == "test-id"
        assert item.name == "Test Item"
        assert item.description == "Test description"
        assert item.price == 99.99
        assert item.category == "test"

    def test_item_model_equality(self):
        """Test ItemModel equality."""
        item1 = ItemModel(
            id="same-id",
            name="Test Item",
            description="Test description",
            price=99.99,
            category="test"
        )

        item2 = ItemModel(
            id="same-id",
            name="Test Item",
            description="Test description",
            price=99.99,
            category="test"
        )

        assert item1 == item2

    def test_item_model_inequality(self):
        """Test ItemModel inequality."""
        item1 = ItemModel(
            id="id-1",
            name="Item 1",
            description="Description 1",
            price=99.99,
            category="test"
        )

        item2 = ItemModel(
            id="id-2",
            name="Item 2",
            description="Description 2",
            price=149.99,
            category="test"
        )

        assert item1 != item2

    def test_item_model_str_representation(self):
        """Test ItemModel string representation."""
        item = ItemModel(
            id="test-id",
            name="Test Item",
            description="Test description",
            price=99.99,
            category="test"
        )

        str_repr = str(item)
        assert "Test Item" in str_repr
        assert "test-id" in str_repr

    def test_item_model_repr_representation(self):
        """Test ItemModel repr representation."""
        item = ItemModel(
            id="test-id",
            name="Test Item",
            description="Test description",
            price=99.99,
            category="test"
        )

        repr_repr = repr(item)
        assert "ItemModel" in repr_repr
        assert "test-id" in repr_repr
        assert "Test Item" in repr_repr
