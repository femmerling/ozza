import errno
import fnmatch
import io
import json
from utils import get_current_miliseconds
from json.decoder import JSONDecodeError
from os import environ
from os import makedirs
from os import path
from os import remove

from exceptions import *


class Ozza(object):
    _data_directory = "data/"
    _data_filename = "default_store.oz"
    _test_filename = "test_store.oz"
    _storage_location = ""
    _in_memory_data = {}
    _test_mode = False

    def __init__(self, test_mode=False):
        self._test_mode = test_mode
        self._init_data_file()

    def get(self, key):
        return self._fetch_matching_resources(key)

    def get_resource_by_id(self, key, id_value):
        result = self.get_resource_by_field_value(key, "id", id_value)
        return result

    def update_resource(self, key, id_value, value):
        result = self._update_item_by_key_id(key, id_value, value)
        return result

    def delete_value_from_resource(self, key, id_value):
        result = self._delete_item_by_key_id(key, id_value)
        return result

    def create_resource(self, key):
        if not key:
            raise EmptyParameterException()
        self._in_memory_data[key] = []
        self._persist_data()

    def add_data(self, key, value):
        if not key or not value:
            raise EmptyParameterException()
        if "id" not in value:
            raise IdNotFoundException()
        if not self._resource_is_available(key):
            self._in_memory_data[key] = []
        value["created_at"] = get_current_miliseconds()
        self._in_memory_data.get(key).append(value)
        self._persist_data()

    def get_resource_by_field_value(self, key, field, value):
        if not key or not field or not value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        if not self._field_is_available(key, field):
            raise FieldNotFoundException()
        value = value.replace("$", "*")
        result = filter(lambda item: fnmatch.fnmatch(item[field], value), self._in_memory_data.get(key))
        return list(result)

    def delete_resource(self, key):
        if not key:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        self._in_memory_data.pop(key, None)
        self._persist_data()

    def _init_data_file(self):
        filename = self._test_filename if self._test_mode else self._data_filename
        if environ.get('DATA_DIRECTORY'):
            self._data_directory = environ.get("DATA_DIRECTORY")
        if environ.get('DATA_FILENAME'):
            self._data_filename = environ.get("DATA_FILENAME")
        self._storage_location = path.join(self._data_directory, filename)
        try:
            with open(self._storage_location, "w") as data:
                self._in_memory_data = json.load(data)
        except io.UnsupportedOperation:
            self._in_memory_data = dict()
            self._persist_data()
        except JSONDecodeError:
            self._in_memory_data = dict()
            self._persist_data()
        except FileNotFoundError:
            self._in_memory_data = dict()
            self._get_or_create_directory()
            self._persist_data()

    def _get_or_create_directory(self):
        try:
            makedirs(self._data_directory)
        except FileExistsError as error:
            if error.errno == errno.EEXIST and path.isdir(self._data_directory):
                pass
            else:
                raise DirectoryCreationException()

    def _persist_data(self):
        try:
            with open(self._storage_location, "w") as data:
                data.write(json.dumps(self._in_memory_data))
        except IOError:
            print("Data can't be written. Waiting for next operation")

    def _resource_is_available(self, key):
        if not key:
            raise EmptyParameterException()
        key = key.replace("$", "*")
        result = fnmatch.filter(self._in_memory_data.keys(), key)
        return len(list(result)) > 0

    def _field_is_available(self, key, field):
        if not key or not field:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        result = filter(lambda item: fnmatch.filter(item.keys(), field), self._in_memory_data.get(key))
        return len(list(result)) > 0


    def _fetch_matching_resources(self, key):
        if not key:
            raise EmptyParameterException()
        key = key.replace("$", "*")
        matching_keys = fnmatch.filter(self._in_memory_data.keys(), key)
        return [value for key, value in self._in_memory_data.items() if key in list(matching_keys)]

    def _update_item_by_key_id(self, key, id_value, value):
        if not key or not id_value or not value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        if "id" not in value.keys():
            raise IdNotFoundException()
        if value.get("id") != id_value:
            raise MismatchIdException()
        for idx, item in enumerate(self._in_memory_data.get(key)):
            if item.get("id") == id_value:
                self._in_memory_data.get(key)[idx] = value
                self._persist_data()
                return self._in_memory_data.get(key)[idx]

    def _delete_item_by_key_id(self, key, id_value):
        if not key or not id_value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        for idx, item in enumerate(self._in_memory_data.get(key)):
            if item.get("id") == id_value:
                del self._in_memory_data.get(key)[idx]
                self._persist_data()
                break
        return "Delete successful"

    def _teardown_data(self):
        if path.exists(self._storage_location):
            remove(self._storage_location)
