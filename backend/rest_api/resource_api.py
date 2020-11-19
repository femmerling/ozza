from sanic.response import json
from rest_api.ozza_api_view import OzzaApiView


class ResourceApi(OzzaApiView):

    async def get(self, request, resource):
        if "filter" in request.args:
            result = await request.ctx.service.get_member_by_value(resource, request.args.get("filter"))
            return json(dict(result=result))
        result = await request.ctx.service.get_resource(resource)
        return json(dict(result=result))

    async def put(self, request, resource):
        expiry = 0
        if "member" in request.args:
            if "expire_in" in request.args:
                expiry = int(request.args.get("expire_in"))
            result = await request.ctx.service.put_member(resource, request.json, expiry)
        else:
            result = await request.ctx.service.put_value(resource, request.json)
        return json(dict(result=result))

    async def post(self, request, resource):
        result = await request.ctx.service.put_value

    async def delete(self, request, resource):
        result = await request.ctx.service.delete_resource(resource)
        return json(dict(result=result))
