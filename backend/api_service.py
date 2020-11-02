from exceptions import ResourceNotFoundException
from ozza import Ozza


class ApiService:

    def __init__(self):
        self.ozza = Ozza()

    async def get_resource(self, key):
        try:
            return self.ozza.get(key)
        except ResourceNotFoundException:
            return []

    async def delete_resource(self, key):
        return self.ozza.delete_resource(key)

    async def add_member_to_resource(self, key, value, expiry=0):
        return self.ozza.add_data(key, value, expiry)

    async def get_member_by_id(self, key, id_value):
        try:
            return self.ozza.get_resource_by_id(key, id_value)
        except ResourceNotFoundException:
            return []

    async def check_member_by_id(self, key, id_value):
        try:
            return self.ozza.member_id_existed(key, id_value)
        except ResourceNotFoundException:
            return False

    async def delete_member_by_id(self, key, id_value):
        try:
            return self.ozza.delete_resource_by_id(key, id_value)
        except ResourceNotFoundException:
            return {}

    async def get_matching_member_by_value(self, key, value):
        return self.ozza.get_member_by_value(key, value)
