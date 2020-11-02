from sanic.response import json, text
from rest_api.ozza_api_view import OzzaApiView


class MemberApi(OzzaApiView):

    async def get(self, request, resource, id_value):
        result = await request.ctx.service.get_member(resource, id_value)
        return json(dict(result=result))

    async def head(self, request, resource, id_value):
        existed = await request.ctx.service.check_member(resource, id_value)
        if existed:
            return text('')
        return text('', status=204)

    async def delete(self, request, resource, id_value):
        result = await request.ctx.service.delete_member(resource, id_value)
        return json(dict(result=result))
