from typing import Dict, Any
from pydantic import BaseModel, validator
from app.contracts.enums import Route


class OzzaResult(BaseModel):
    result: Dict[str, Any]


class ResourceData(BaseModel):
    value: dict
    route: Route
    expire_in: int = 0

    @validator('value')
    def value_must_contain_id(cls, value):
        if 'id' not in value.keys():
            raise ValueError('`value` must contain `id` field')
        return value
