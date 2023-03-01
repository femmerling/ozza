from fastapi import APIRouter
from app.services import ozza_service
from app.contracts.resource_data import ResourceData, OzzaResult
from app.contracts.enums import Route


router = APIRouter()


@router.get('/{resource_id}')
async def get_resource(resource_id: str, f: str | None = None) -> OzzaResult:
    result = {}
    if f:
        result = await ozza_service.get_member_by_value(resource_id, f)
    else:
        result = await ozza_service.get_member(resource_id)
    return OzzaResult(result=result)


@router.put('/{resource_id}')
async def put_resource(resource_id: str, data: ResourceData) -> OzzaResult:
    result = {}
    if data.route == Route.RESOURCE:
        result = await ozza_service.put_value(resource_id, data.value, data.expire_in)
    else:
        result = await ozza_service.put_member(resource_id, data.value)
    return OzzaResult(result=result)
