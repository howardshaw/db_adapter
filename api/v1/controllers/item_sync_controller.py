from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from api.v1.schemas.item_schema import ItemSchema, ItemCreateSchema
from container import Container
from services.item_sync_service import SyncItemService

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/", response_model=list[ItemSchema])
@inject
def list_items(service: SyncItemService = Depends(Provide[Container.sync_item_service])):
    return [ItemSchema.model_validate(entity.model_dump()) for entity in service.list()]


@router.get("/{item_id}", response_model=ItemSchema)
@inject
def get_item(item_id: str, service: SyncItemService = Depends(Provide[Container.sync_item_service])):
    entity = service.get(item_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemSchema.model_validate(entity.model_dump())


@router.post("/", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
@inject
def create_item(data: ItemCreateSchema, service: SyncItemService = Depends(Provide[Container.sync_item_service])):
    entity = service.create(data)
    return ItemSchema.model_validate(entity.model_dump())


@router.put("/{item_id}", response_model=ItemSchema)
@inject
def update_item(item_id: str, data: ItemCreateSchema,
                service: SyncItemService = Depends(Provide[Container.sync_item_service])):
    entity = service.update(item_id, data)
    if not entity:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemSchema.model_validate(entity.model_dump())


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_item(item_id: str, service: SyncItemService = Depends(Provide[Container.sync_item_service])):
    ok = service.delete(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
