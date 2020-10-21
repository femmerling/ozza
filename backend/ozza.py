import errno
import fnmatch
import json
from json.decoder import JSONDecodeError
from os import environ
from os import makedirs
from os import path
from os import remove

from exceptions import *
from utils import get_unix_millis, current_utctime, get_expiry_time


class Ozza(object):
    """
    Data store manager business logic object.
    Will store data into *.oz file.
    Set directory and filename using environment variables
    Use `DATA_DIRECTORY` for data store directory
    Use `DATA_FILENAME` for data filename. Should end with *.oz
    Data structure use is dictionary of resources, marked by `key` parameters throughout this class.
    Each resource  will contain a list of members.
    Each member is a dictionary.
    Each member must have an `id` field as an identifier. Data type of `id` value is not defined
    """
    _data_directory = "data/"
    _data_filename = "default_store.oz"
    _test_filename = "test_store.oz"
    _storage_location = ""
    _in_memory_data = {}
    _test_mode = False

    def __init__(self, test_mode=False):
        """
        Initializer for logger. Just need to do this once and reuse the object.
        Will initialize data file if file not available and will load data if data file existed
        Args:
            test_mode: Boolean, to determine whether this is in test mode or not
        """
        self._test_mode = test_mode
        self._init_data_file()

    def get(self, key):
        """
        Retrieves a complete data collection based on resource group key
        Args:
            key: String, identifier of resource. Can accept wildcard `$` for any amount of characters in between
        Returns:
            list of dictionary object of the requested resource identifier
        """
        return self._fetch_matching_resources(key)

    def get_resource_by_id(self, key, id_value):
        """
        Returns matching resource members by given member id
        Args:
            key: String, identifier of resource
            id_value: String, value of `id` in member. Can accept wildcard `$` for any amount of characters in between
        Returns:
            list of dictionary object of the matching member identifier
        """
        result = self.get_resource_by_field_value(key, "id", id_value)
        return result

    def update_resource(self, key, id_value, value):
        """
        Updates the member data of a given resource and member id
        Args:
            key: String, identifier of resource
            id_value: String, value of `id` in member. Must be exact match, does not accept wildcard
            value: value that needs to be updated
        Returns:
            Updated member data, a dictionary
        """
        result = self._update_item_by_key_id(key, id_value, value)
        return result

    def delete_value_from_resource(self, key, id_value):
        """
        Deletes a member from a given resource
        Args:
            key: String, identifier of resource
            id_value: String, value of `id` in member. Must be exact match, does not accept wildcard
        Returns:
            String result message
        """
        result = self._delete_item_by_key_id(key, id_value)
        return result

    def create_resource(self, key):
        """
        Creates a resource space in the storage with empty members
        Args:
            key: String, identifier of resource
        """
        if not key:
            raise EmptyParameterException()
        self._in_memory_data[key] = []
        self._persist_data()

    def add_data(self, key, value, expiry=0):
        """
        Add a new member data to a resource
        Args:
            key: String, identifier of resource
            value: Dictionary, data to be added. Must contain `id` field
            expiry: Int, Expiry time in minutes. 0 means no expiry set.
        Returns:
            Member dictionary object added
        """
        if not key or not value:
            raise EmptyParameterException()
        if "id" not in value:
            raise IdNotFoundException()
        if not self._resource_is_available(key):
            self._in_memory_data[key] = []
        creation_time = current_utctime()
        value["created_at"] = get_unix_millis(current_utctime())
        value["expiry_time"] = get_expiry_time(expiry, creation_time) if expiry > 0 else 0
        if self.member_id_existed(key, value.get("id")):
            self._update_item_by_key_id(key, value.get("id"), value)
        else:
            self._in_memory_data.get(key).append(value)
        self._persist_data()
        value_id = value.get("id")
        return self.get_resource_by_id(key, value_id)[0]

    def get_resource_by_field_value(self, key, field, value):
        """
        Retrieve a resource member by specified field and field value.
        Field value should be string. Value can accept wildcard `$` for any amount of characters in between
        Args:
            key: String, identifier of resource
            field: String, field name
            value: String, field value. Can accept wildcard `$` for any amount of characters in between
        Returns:
            list of dictionary object of the matching requested field value
        """
        if not key or not field or not value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        if not self._field_is_available(key, field):
            raise FieldNotFoundException()
        value = value.replace("$", "*")
        result = filter(
            lambda item: fnmatch.fnmatch(item[field], value) and self._expiry_is_valid(item),
            self._in_memory_data.get(key))
        return list(result)

    def _expiry_is_valid(self, item):
        """
        Performs check if expiry time is valid.
        Args:
            item: Dictionary, member object
        Returns:
            Boolean, expired or not if conditions are met
        """
        if item.get("expiry_time") == 0:
            return True
        else:
            return get_unix_millis(current_utctime()) < item.get("expiry_time")

    def delete_resource(self, key):
        """
        Delete a resource by given key
        Args:
            key: String, identifier of resource
        Returns:
            String, deletion message
        """
        if not key:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        self._in_memory_data.pop(key, None)
        self._persist_data()
        return "Resource deleted"

    def delete_resource_by_id(self, key, id_value):
        """
        Deletes a member from a given resource
        Args:
            key: String, identifier of resource
            id_value: String, value of `id` in member. Must be exact match, does not accept wildcard
        Returns:
            String result message
        """
        result = self._delete_item_by_key_id(key, id_value)
        return result

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
                self._in_memory_data = json.load(data)
        except IOError:
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
        """
        Searched for assigned directory. If not found will create new
        """
        try:
            makedirs(self._data_directory)
        except FileExistsError as error:
            if error.errno == errno.EEXIST and path.isdir(self._data_directory):
                pass
            else:
                print("Can't create directory, please check permission")

    def _persist_data(self):
        """
        Writes the data from the memory into storage so on restart data is persisted.
        """
        try:
            with open(self._storage_location, "w") as data:
                data.write(json.dumps(self._in_memory_data))
        except IOError:
            print("Data can't be written. Waiting for next operation")

    def _resource_is_available(self, key):
        """
        Checks if a given resource is available in the data
        Args:
            key: String, identifier of resource. Can accept wildcard `$` for any amount of characters in between
        Returns:
            Boolean, indicating resource existed or not
        """
        if not key:
            raise EmptyParameterException()
        key = key.replace("$", "*")
        result = fnmatch.filter(self._in_memory_data.keys(), key)
        return len(list(result)) > 0

    def _field_is_available(self, key, field):
        """
        Checks if a given field is available in the resource
        Args:
            key: String, identifier of resource.
            field: String, field name. Does not accept wildcard
        Returns:
            Boolean, indicating field existed or not
        """
        if not key or not field:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        result = filter(lambda item: fnmatch.filter(item.keys(), field), self._in_memory_data.get(key))
        return len(list(result)) > 0

    def _fetch_matching_resources(self, key):
        """
        Retrieves a complete data collection based on resource group key
        Args:
            key: String, identifier of resource. Can accept wildcard `$` for any amount of characters in between
        Returns:
            list of dictionary object of the requested resource identifier
        """
        if not key:
            raise EmptyParameterException()
        key = key.replace("$", "*")
        matching_keys = fnmatch.filter(self._in_memory_data.keys(), key)
        data = []
        for matching_key in matching_keys:
            [data.append(item) for item in self._in_memory_data.get(matching_key)]
        return data

    def _update_item_by_key_id(self, key, id_value, value):
        """
        Updates the member data of a given resource and member id
        Args:
            key: String, identifier of resource
            id_value: String, value of `id` in member. Must be exact match, does not accept wildcard
            value: value that needs to be updated
        Returns:
            Updated member data, a dictionary
        """
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
                for field_key in value.keys():
                    item[field_key] = value[field_key]
                self._in_memory_data.get(key)[idx] = item
                self._persist_data()
                return self._in_memory_data.get(key)[idx]

    def _delete_item_by_key_id(self, key, id_value):
        """
        Deletes a member from a given resource
        Args:
            key: String, identifier of resource
            id_value: String, value of `id` in member. Must be exact match, does not accept wildcard
        Returns:
            String result message
        """
        if not key or not id_value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        deleted = False
        for idx, item in enumerate(self._in_memory_data.get(key)):
            if item.get("id") == id_value:
                del self._in_memory_data.get(key)[idx]
                self._persist_data()
                deleted = True
                break
        if deleted:
            return "Delete successful"
        else:
            return "Member not found"

    def member_id_existed(self, key, id_value):
        """
        Checks if an id exist at a given resource
        Args:
            key: String, identifier of the resource
            id_value: String, member id value to check

        Returns:

        """
        if not key or not id_value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        result = filter(lambda item: item.get("id") == id_value, self._in_memory_data.get(key))
        result = list(result)
        return len(list(result)) > 0

    def _teardown_data(self):
        """
        Deletes the data file being used to store. Consider this a total data reset.
        Useful for testing purposes
        """
        if path.exists(self._storage_location):
            remove(self._storage_location)

    def get_member_by_value(self, key, value):
        """
        Filters any members by value given
        Args:
            key: String, identifier of resource
            value: String, expected filter value
        Returns:
            List of matching members
        """
        if not key or not value:
            raise EmptyParameterException()
        if not self._resource_is_available(key):
            raise ResourceGroupNotFoundException()
        value = value.replace("$", "*")
        result = filter(lambda item: fnmatch.filter(self._stringify_value_list(item), value), self.get(key))
        return list(result)

    def _stringify_value_list(self, data_dict):
        return [str(value) if type(value) is not str else value for value in list(data_dict.values())]
