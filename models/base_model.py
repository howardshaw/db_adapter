import uuid
from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore', arbitrary_types_allowed=True)
    id: str = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


M = TypeVar('M', bound=BaseModel)
