import time
from datetime import datetime

from sanic import Sanic
from sanic.response import json, text

from _api_service import ApiService


def create_api():
    service = ApiService()
    api = Sanic(name="API", configure_logging=False)

    """
    API middleware is used to handle logging output. Default logging does not provide enough information for metrics
    """
    @api.middleware('request')
    async def embed_start_time(request):
        request.ctx.start_time = time.time()

    @api.middleware('response')
    async def log_request(request, response):
        spend_time = round((time.time() - request.ctx.start_time) * 1000)
        print("[{}] [ACCESS] LEN:{}b\tLAT:{}ms IP:{} STATUS:{} {}\t{} {}".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            len(response.body),
            spend_time,
            request.headers.get('remote_addr'),
            response.status,
            request.method,
            request.path,
            request.query_string
        ))

    @api.route("/<key>", methods=["GET", "PUT", "DELETE"])
    async def resource_endpoint(request, key):
        result = None
        if request.method == "GET":
            if "filter" in request.args:
                result = await service.get_matching_member_by_value(key, request.args.get("filter"))
            else:
                result = await service.get_resource(key)

        elif request.method == "DELETE":
            result = await service.delete_resource(key)
        elif request.method == "PUT":
            expiry = 0
            if "expire_in" in request.args:
                expiry = int(request.args.get("expire_in"))
            result = await service.add_member_to_resource(key, request.json, expiry)
        return json({"result": result})

    @api.route("/<key>/<id>", methods=["GET", "HEAD", "DELETE"])
    async def member_endpoint(request, key, id):
        result = None
        if request.method == "GET":
            result = await service.get_member_by_id(key, id)
        elif request.method == "HEAD":
            existed = await service.check_member_by_id(key, id)
            if existed:
                return text('')
            return text('', status=204)
        elif request.method == "DELETE":
            result = await service.delete_member_by_id(key, id)
        return json({"result": result})

    return api
