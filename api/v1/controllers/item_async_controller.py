from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject
from api.v1.schemas.item_schema import ItemSchema, ItemCreateSchema
from services.item_async_service import AsyncItemService
from container import Container

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/", response_model=list[ItemSchema])
@inject
async def list_items(service: AsyncItemService = Depends(Provide[Container.async_item_service])):
    return [ItemSchema.model_validate(entity.model_dump()) for entity in await service.list()]


@router.get("/{item_id}", response_model=ItemSchema)
@inject
async def get_item(item_id: str, service: AsyncItemService = Depends(Provide[Container.async_item_service])):
    entity = await service.get(item_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemSchema.model_validate(entity.model_dump())


@router.post("/", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
@inject
async def create_item(data: ItemCreateSchema, service: AsyncItemService = Depends(Provide[Container.async_item_service])):
    entity = await service.create(data)
    return ItemSchema.model_validate(entity.model_dump())


@router.put("/{item_id}", response_model=ItemSchema)
@inject
async def update_item(item_id: str, data: ItemCreateSchema, service: AsyncItemService = Depends(Provide[Container.async_item_service])):
    entity = await service.update(item_id, data)
    if not entity:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemSchema.model_validate(entity.model_dump())


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_item(item_id: str, service: AsyncItemService = Depends(Provide[Container.async_item_service])):
    ok = await service.delete(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
