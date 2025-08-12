import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from config import get_settings
from container import Container
from infras.repositories.base_po import BasePO
from infras.repositories.factory import get_engine

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ApiServer")

container = Container()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine(settings)
    if settings.USE_ASYNC_DB:
        async with engine.begin() as conn:
            await conn.run_sync(BasePO.metadata.create_all)
    else:
        BasePO.metadata.create_all(bind=engine)

    yield

    if settings.USE_ASYNC_DB:
        await engine.dispose()
    else:
        engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


if settings.USE_ASYNC_ROUTER:
    from api.v1.controllers import item_async_controller as item

    app.include_router(item.router)
else:
    from api.v1.controllers import item_sync_controller as item

    app.include_router(item.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
