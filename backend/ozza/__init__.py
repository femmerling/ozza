import errno
import json
from json.decoder import JSONDecodeError
from os import environ
from os import makedirs
from os import path
from os import remove

class Ozza:
    _data_directory = "data/"
    _data_filename = "default_store.oz"
    _test_filename = "test_store.oz"
    _storage_location = ""
    _memory_data = {}
    _test_mode = False

    def __init__(self, test_mode=False):
        self._test_mode = test_mode
        self._init_data_file()

    def _init_data_file(self):
        if environ.get("DATA_DIRECTORY"):
            self._data_directory = environ.get("DATA_DIRECTORY")
        if environ.get("DATA_FILENAME"):
            self._data_filename = environ.get("DATA_FILENAME")
        filename = self._test_filename if self._test_mode else self._data_filename
        self._storage_location = path.join(self._data_directory, filename)
        try:
            with open(self._storage_location) as data:
                self._memory_data = json.load(data)
        except FileNotFoundError:
            self._memory_data = dict()
            self._get_or_create_directory()
            self._persist_data()
        except (IOError, JSONDecodeError):
            self._memory_data = dict()
            self._persist_data()

    def _get_or_create_directory(self):
        try:
            makedirs(self._data_directory)
        except FileExistsError as error:
            if error.errno == errno.EEXIST and path.isdir(self._data_directory):
                print("Directory already exist.")
            else:
                print("Can't create directoy, please check permission")

    def _persist_data(self):
        try:
            with open(self._storage_location, "w") as data:
                data.write(json.dumps(self._memmory_data))
        except IOError:
            print("Data can't be written. Possible I/O error or permission issue")

    def get_resource(self, key):
        pass

    def create_resource(self, key):
        pass

    def delete_resource(self, key):
        pass

    def check_resource(self, key):
        pass

    def get_member(self, key, id_value):
        pass

    def update_or_create_member(self, key, member_value, expiry=0):
        pass

    def delete_member(self, key, id_value):
        pass

    def check_member(self, key, id_value):
        pass

    def filter_member(self, key, value):
        pass

    def multiple_filter_member(self, key, filter_list):
        pass

    def _resource_is_available(self, key):
        pass

    def _member_key_is_available(self,key, field):
        pass

    def _fetch_matching_resource(self, key):
        pass

    def _fetch_matching_member_by_field(self, key, value, field="id"):
        pass

    def _fetch_matching_member_by_value(self, key, value):
        pass
