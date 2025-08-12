import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestItemAPI:
    """Test cases for Item API endpoints."""

    def test_list_items_empty(self, test_client: TestClient):
        """Test listing items when database is empty."""
        response = test_client.get("/items/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_item_not_found(self, test_client: TestClient):
        """Test getting a non-existent item."""
        response = test_client.get("/items/non-existent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Item not found"

    def test_create_item_success(self, test_client: TestClient, sample_item_data: dict):
        """Test creating a new item successfully."""
        response = test_client.post("/items/", json=sample_item_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["name"] == sample_item_data["name"]
        assert data["description"] == sample_item_data["description"]
        assert data["price"] == sample_item_data["price"]
        assert data["category"] == sample_item_data["category"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_item_invalid_data(self, test_client: TestClient):
        """Test creating item with invalid data."""
        invalid_data = {"name": "", "price": -10}  # Invalid data
        response = test_client.post("/items/", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_item_success(self, test_client: TestClient, sample_item_data: dict):
        """Test updating an existing item."""
        # First create an item
        create_response = test_client.post("/items/", json=sample_item_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        item_id = create_response.json()["id"]

        # Update the item
        update_data = {
            "name": "Updated Item",
            "description": "Updated description",
            "price": 150.00,
            "category": "updated"
        }
        response = test_client.put(f"/items/{item_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["price"] == update_data["price"]
        assert data["category"] == update_data["category"]

    def test_update_item_not_found(self, test_client: TestClient, sample_item_data: dict):
        """Test updating a non-existent item."""
        response = test_client.put("/items/non-existent-id", json=sample_item_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Item not found"

    def test_delete_item_success(self, test_client: TestClient, sample_item_data: dict):
        """Test deleting an existing item."""
        # First create an item
        create_response = test_client.post("/items/", json=sample_item_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        item_id = create_response.json()["id"]

        # Delete the item
        response = test_client.delete(f"/items/{item_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify item is deleted
        get_response = test_client.get(f"/items/{item_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_item_not_found(self, test_client: TestClient):
        """Test deleting a non-existent item."""
        response = test_client.delete("/items/non-existent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Item not found"

    def test_crud_operations_flow(self, test_client: TestClient, sample_items_data: list):
        """Test complete CRUD operations flow."""
        # Create multiple items
        created_items = []
        for item_data in sample_items_data:
            response = test_client.post("/items/", json=item_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_items.append(response.json())

        # List all items
        response = test_client.get("/items/")
        assert response.status_code == status.HTTP_200_OK
        items = response.json()
        assert len(items) == len(sample_items_data)

        # Get specific item
        first_item = created_items[0]
        response = test_client.get(f"/items/{first_item['id']}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == first_item["id"]

        # Update item
        update_data = {
            "name": "Updated Name",
            "description": "Updated description",
            "price": 999.99,
            "category": "premium"
        }
        response = test_client.put(f"/items/{first_item['id']}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        updated_item = response.json()
        assert updated_item["name"] == update_data["name"]
        assert updated_item["price"] == update_data["price"]

        # Delete item
        response = test_client.delete(f"/items/{first_item['id']}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify item is deleted
        response = test_client.get(f"/items/{first_item['id']}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.integration
    def test_api_health_check(self, test_client: TestClient):
        """Test API health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"

    @pytest.mark.integration
    def test_api_docs_available(self, test_client: TestClient):
        """Test that API documentation is available."""
        response = test_client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

        response = test_client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
