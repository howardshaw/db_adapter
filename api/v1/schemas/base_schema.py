import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Primary key")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Update time")
