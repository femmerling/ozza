import errno
import fnmatch
import json
from os import environ
from os import makedirs
from os import path
from os import remove
from json.decoder import JSONDecodeError

from ozza.exceptions import EmptyParameterException
from ozza.exceptions import FieldNotFoundException
from ozza.exceptions import IdNotFoundException
from ozza.exceptions import InvalidFilterFormatException
from ozza.exceptions import ResourceNotFoundException
from utils import current_utctime
from utils import get_expiry_time
from utils import get_timestamp_from_millis
from utils import get_unix_millis


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
        """
                Initialization of data file. If directory and file does not exist will create it.
                If directory and file already exist will load data into memory.
                """
        filename = self._test_filename if self._test_mode else self._data_filename
        if environ.get("DATA_DIRECTORY"):
            self._data_directory = environ.get("DATA_DIRECTORY")
        if environ.get("DATA_FILENAME"):
            self._data_filename = environ.get("DATA_FILENAME")
        self._storage_location = path.join(self._data_directory, filename)
        try:
            with open(self._storage_location) as data:
                self._memory_data = json.load(data)
        except FileNotFoundError:
            self._memory_data = dict()
            self._get_or_create_directory()
            self._persist_data()
        except IOError:
            self._memory_data = dict()
            self._persist_data()
        except JSONDecodeError:
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
                data.write(json.dumps(self._memory_data))
        except IOError:
            print("Data can't be written. Waiting for next operation")

    def get_resource(self, key):
        return self._fetch_matching_resource(key)

    def create_resource(self, key):
        if not key:
            raise EmptyParameterException()
        self._memory_data[key] = []
        self._persist_data()

    def delete_resource(self, key):
        if not key:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceNotFoundException()
        self._memory_data.pop(key, None)
        self._persist_data()
        return "Resource deleted"

    def check_resource(self, key):
        return self._resource_is_available(key)

    def get_member(self, key, id_value):
        result = self._fetch_matching_member_by_field(key, id_value)
        print(result)
        return result[0] if len(result) > 0 else []

    def put_member(self, key, member_value, expiry=0):
        if not key or not member_value:
            raise EmptyParameterException()
        if "id" not in member_value.keys():
            raise IdNotFoundException()
        if not self._resource_is_available(key):
            self.create_resource(key)
        if self._member_id_existed(key, member_value.get("id")):
            return self._update_member(key, member_value, expiry)
        else:
            return self._create_member(key, member_value, expiry)

    def delete_member(self, key, id_value):
        if not key or not id_value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceNotFoundException()
        for idx, member in enumerate(self._memory_data.get(key)):
            if member.get("id") == id_value:
                del self._memory_data[key][idx]
                self._persist_data()
                return "Delete successful"
        return "Member not found"

    def check_member(self, key, id_value):
        return self._member_id_existed(key, id_value)

    def get_member_by_field_value(self, key, field, value):
        return self._fetch_matching_member_by_field(key, value, field)

    def get_member_by_value(self, key, field_value):
        return self._fetch_matching_member_by_value(key, field_value)

    def multiple_filter_member(self, key, filter_list, condition="and"):
        if condition == "and":
            return self._filter_and(key, filter_list)
        else:
            return self._filter_or(key, filter_list)

    def _create_member(self, key, member_value, expiry=0):
        creation_time = current_utctime()
        member_value["created_at"] = get_unix_millis(creation_time)
        member_value["expiry_time"] = get_expiry_time(expiry, creation_time) if expiry > 0 else 0
        self._memory_data[key].append(member_value)
        self._persist_data()
        return self.get_member(key, member_value.get("id"))

    def _update_member(self, key, member_value, expiry=0):
        if not key or not member_value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceNotFoundException()
        current_member = self.get_member(key, member_value.get("id"))
        member_value["created_at"] = current_member.get("created_at")
        creation_time = get_timestamp_from_millis(current_member.get("created_at"))
        member_value["expiry_time"] = get_expiry_time(expiry, creation_time) if expiry > 0 else 0
        for idx, member in enumerate(self._memory_data.get(key)):
            if member.get("id") == member_value.get("id"):
                for field_key in member_value.keys():
                    member[field_key] = member_value[field_key]
                self._memory_data[key][idx] = member
                self._persist_data()

                return self._memory_data[key][idx]

    def _resource_is_available(self, key):
        if not key:
            raise EmptyParameterException()
        return key in self._memory_data.keys()

    def _member_id_existed(self, key, id_value):
        if not key and not id_value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceNotFoundException()
        result = filter(lambda item: item.get("id") == id_value, self.get_resource(key))
        return len(list(result)) > 0

    def _field_existed(self, key, field):
        if not key or not field:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceNotFoundException()
        result = filter(lambda item: fnmatch.filter(item.keys(), field), self.get_resource(key))
        return len(list(result)) > 0

    def _member_key_is_available(self, key, field):
        if not key and not field:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceNotFoundException()
        result = filter(lambda item: fnmatch.filter(item.keys(), field), self._memory_data.get(key))
        return len(list(result)) > 0

    def _fetch_matching_resource(self, key):
        if not key:
            raise EmptyParameterException()
        matched_keys = fnmatch.filter(self._memory_data.keys(), key)
        data = []
        for matched_key in matched_keys:
            [data.append(item) for item in self._memory_data.get(matched_key)]
        return data

    def _fetch_matching_member_by_field(self, key, value, field="id"):
        if not key or not value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceNotFoundException()
        if not self._field_existed(key, field):
            raise FieldNotFoundException()
        result = filter(lambda item: fnmatch.fnmatch(item.get(field), value) and self._not_expired(item),
                        self.get_resource(key))
        return list(result)

    def _fetch_matching_member_by_value(self, key, value):
        if not key and not value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceNotFoundException()
        result = filter(lambda item: fnmatch.filter(self._stringify_dictionary_values(item), value),
                        self.get_resource(key))
        return list(result)

    def _stringify_dictionary_values(self, data_dict):
        if not data_dict:
            raise EmptyParameterException()
        return [str(value) if type(value) is not str else value for value in list(data_dict.values())]

    def _not_expired(self, item):
        if not item:
            raise EmptyParameterException()
        if item.get("expiry_time") == 0:
            return True
        else:
            return get_unix_millis(current_utctime()) < item.get("expiry_time")

    def _filters_are_valid(self, filter_list, key):
        for item in filter_list:
            if "field" not in item.keys() or "value" not in item.keys():
                return False
            if not self._field_existed(key, item.get("field")):
                return False
        return True

    def _filter_and(self, key, filter_list):
        if not key or not filter_list:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceNotFoundException()
        if not self._filters_are_valid(filter_list, key):
            raise InvalidFilterFormatException()
        is_start = True
        result = []
        for filter_item in filter_list:
            if is_start:
                filter_result = filter(lambda item: item.get(filter_item.get("field")) == filter_item.get("value"),
                                       self.get_resource(key))
                filter_result = list(filter_result)
                [result.append(item) for item in filter_result]
                print("is start result {}".format(result))
                is_start = False
            else:
                if len(result) == 0:
                    return []
                filter_result = filter(lambda item: item.get(filter_item.get("field")) == filter_item.get("value"),
                                       result)
                result=list(filter_result)
                print("non is start result {}".format(result))
        return result

    def _filter_or(self, key, filter_list):
        if not key or not filter_list:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceNotFoundException()
        if not self._filters_are_valid(filter_list, key):
            raise InvalidFilterFormatException()
        result = []
        for filter_item in filter_list:
            filter_result = filter(lambda item: item.get(filter_item.get("field")) == filter_item.get("value"),
                                   self.get_resource(key))
            [result.append(item) for item in filter_result if item not in result]
        return result

    def _teardown_data(self):
        if path.exists(self._storage_location):
            remove(self._storage_location)
