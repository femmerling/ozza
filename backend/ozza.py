import errno
import fnmatch
import json
from datetime import datetime
from exceptions import *
from json.decoder import JSONDecodeError
from os import environ
from os import path
from os import makedirs


class Ozza(object):
    _data_directory = "data/"
    _data_filename = "default_store.oz"
    _test_filename = "test_store.oz"
    _storage_location = ""
    _in_memory_data = {}
    _test_mode = False

    def __init__(self, test_mode = False):
        self._test_mode = test_mode
        self._init_data_file()

    def get(self, key):
        if not key:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        return self._fetch_matching_resources(key)

    def get_resource_by_id(self, key, id):
        if not key or not id:
            raise EmptyParameterException()
        if not self._resource_is_available:
            raise ResourceGroupNotFoundException()
        pass

    def update_resorce(self, key, id, value):
        if not key or not id or not value:
            raise EmptyParameterException()
        pass

    def delete_resource(self, key, id, value):
        if not key or not id or not value:
            raise EmptyParameterException()
        pass

    def add_data(self, key, value):
        if not key or not value:
            raise EmptyParameterException()
        if "id" not in value:
            raise IdNotFoundException()
        if not self._resource_is_available(key):
            self._in_memory_data[key] = []
        value["created_at"] = self._current_unixtime
        self._in_memory_data.get(key).append(value)
        self._persist_data()

    def get_resource_by_field_value(self, key, field, value):
        if not key or not field or not value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        if not self._field_is_available():
            raise FieldNotFoundException()
        value = value.replace("$", "*")
        result = filter(
            lambda item: fnmatch.fnmatch(item[field], value), self._in_memory_data.get(key))
        return {key: list(result)}

    def delete_from_cache(self, key):
        if not key:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        self._in_memory_data.pop(key, None)
        self._persist_data()

    def _persist_data(self):
        try:
            with open(self._storage_location, "w") as data:
                data.write(json.dumps(self._in_memory_data))
        except DataWriteException:
            print("Data can't be written. Waiting for next operation")

    def _init_data_file(self):
        filename = self._test_filename if self._test_mode else self._data_filename
        if environ.get('DATA_DIRECTORY'):
            self._data_directory = environ.get("DATA_DIRECTORY")
        if environ.get('DATA_FILENAME'):
            self._data_filename = environ.get("DATA_FILENAME")
        try:
            self._get_or_create_directory()
            self._storage_location = path.join(self._data_directory, filename)
        except:
            self._storage_location = filename
        finally:
            try:
                with open(self._storage_location, "w") as data:
                    self._in_memory_data = json.load(data)
            except DataWriteException:
                print("Data load error. Creating new file..")
                with open(self._storage_location, "w") as data:
                    data.write("")
            except JSONDecodeError:
                print("Data can't be decoded. Creating new file..")
                with open(self._storage_location, "w") as data:
                    data.write("")

    def _get_or_create_directory(self):
        try:
            makedirs(self._data_directory)
        except DirectoryOperationException as error:
            if error.errno == errno.EEXIST and path.isdir(path):
                pass
            else:
                raise DirectoryCreationException()

    def _resource_is_available(self, key):
        if not key:
            raise EmptyParameterException()
        key = key.replace("$","*")
        result = fnmatch.filter(self._in_memory_data.keys(), key)
        return len(list(result)) > 0

    def _field_is_available(self, key, field):
        if not key or not field:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        result = filter(
            lambda item: fnmatch.filter(item.keys(), field), self._in_memory_data.get(key))
        return len(list(result)) > 0

    def _current_unixtime(self):
        epoch = datetime.utcfromtimestamp(0)
        return (datetime.utcnow() - epoch).total_seconds * 1000

    def _fetch_matching_resources(self, key):
        if not key:
            raise EmptyParameterException()
        key = key.replace("$","*")
        matching_keys = fnmatch.filter(self._in_memory_data.keys(), key)
        return {
            key: value for key,value in self._in_memory_data.items() if key in list(matching_keys)}
