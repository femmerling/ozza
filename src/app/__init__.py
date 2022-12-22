import time
from datetime import datetime

from fastapi import FastAPI
#from sanic import Sanic

from rest_api.api_service import ApiService
from rest_api.member_api import MemberApi
from rest_api.resource_api import ResourceApi


def create_api():
    service = ApiService()
    api = FastAPI()


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

    api.add_route(ResourceApi.as_view(service=service), "/<resource>")
    api.add_route(MemberApi.as_view(service=service), "/<resource>/<id_value>")

    return api


