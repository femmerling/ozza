import errno
import json
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

    def get_data_by_key(self, key):
        if key in self._in_memory_data:
            return self._in_memory_data.get(key)
        return {}

    def add_data(self, key, value):
        self._in_memory_data[key] = value
        self._persist_data()

    def delete_from_cache(self, key):
        self._in_memory_data.pop(key, None)
        self._persist_data()

    def _persist_data(self):
        with open(self._storage_location, "w") as data:
            data.write(json.dumps(self._in_memory_data))

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
            except IOError:
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
        except OSError as error:
            if error.errno == errno.EEXIST and path.isdir(path):
                pass
            else:
                raise Exception("Can't create directory")
