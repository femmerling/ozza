from ozza.exceptions import ResourceNotFoundException
from ozza import Ozza


class ApiService:

    def __init__(self):
        self.ozza = Ozza()

    async def get_resource(self, key):
        try:
            return self.ozza.get_resource(key)
        except ResourceNotFoundException:
            return []

    async def delete_resource(self, key):
        return self.ozza.delete_resource(key)

    async def put_member(self, key, member_value, expiry=0):
        return self.ozza.put_member(key, member_value, expiry)

    async def get_member(self, key, id_value):
        try:
            return self.ozza.get_member(key, id_value)
        except ResourceNotFoundException:
            return []

    async def put_value(self, key, value):
        return self.ozza.put_value(key, value)

    async def check_member(self, key, id_value):
        try:
            return self.ozza.check_member(key, id_value)
        except ResourceNotFoundException:
            return False

    async def delete_member(self, key, id_value):
        try:
            return self.ozza.delete_member(key, id_value)
        except ResourceNotFoundException:
            return {}

    async def get_member_by_value(self, key, value):
        return self.ozza.get_member_by_value(key, value)
