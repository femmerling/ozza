import os
import time
import unittest

from ozza import Ozza
from ozza.exceptions import *


class OzzaTest(unittest.TestCase):

    def setUp(self):
        self.ozza = Ozza(test_mode=True)

    def test_creation(self):
        self.assertEqual(self.ozza._memory_data, {})

    def test_json_decode_error(self):
        os.environ["DATA_DIRECTORY"] = "tests/"
        os.environ["DATA_FILENAME"] = "brokenjson.oz"
        db = Ozza()
        self.assertEqual(db._memory_data, {})

    def test_create_resource(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.create_resource(None)

        self.ozza.create_resource("test-data")
        self.assertTrue("test-data" in self.ozza._memory_data)

    def test_add_data(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.put_member(None, None)

        with self.assertRaises(IdNotFoundException):
            data = dict(name="some-name")
            self.ozza.put_member("test-set", data)

        data = dict(id="some-id", name="some-name")
        self.ozza.put_member("test-set", data)
        resource_set = self.ozza.get_resource("test-set")
        self.assertEqual(resource_set[0].get("name"), data.get("name"))
        resource_set = self.ozza.get_resource("t*t")
        self.assertEqual(resource_set[0].get("name"), data.get("name"))
        data2 = dict(id="some-id2", name="some-name2")
        self.ozza.put_member("test-set", data2)
        resource_set = self.ozza.get_resource("test-set")
        self.assertEqual(resource_set[1].get("name"), data2.get("name"))

    def test_update_resource(self):
        self.ozza.create_resource("test-data")
        with self.assertRaises(EmptyParameterException):
            self.ozza.put_member(None, None)
        with self.assertRaises(IdNotFoundException):
            self.ozza.put_member("test-data", {"key": "value"})
        data = dict(id="some-id", name="some-name")
        self.ozza.put_member("test-data", data)
        data["name"] = "some-updated-name"
        result = self.ozza.put_member("test-data", data)
        print(self.ozza.get_resource("test-data"))
        self.assertEqual(data.get("name"), result.get("name"))

    def test_delete_value_from_resource(self):
        data = dict(id="some-id", name="some-name")
        self.ozza.put_member("test-data", data)
        data = dict(id="some-id2", name="some-name")
        self.ozza.put_member("test-data", data)
        self.ozza.delete_member("test-data", "some-id")
        result = self.ozza.get_member("test-data", "some-id")
        self.assertEqual(result, [])

    def test_delete_resource(self):
        self.ozza.create_resource("test-data")
        with self.assertRaises(EmptyParameterException):
            self.ozza.delete_resource(None)
        with self.assertRaises(ResourceNotFoundException):
            self.ozza.delete_resource("not found")
        result = self.ozza.delete_resource("test-data")
        self.assertEqual(result, "Resource deleted")

    def test_get_resource_by_field_value(self):
        data = dict(id="some-id", name="some-name")
        self.ozza.put_member("test-data", data)
        with self.assertRaises(EmptyParameterException):
            self.ozza.get_member_by_field_value(None, None, None)
        with self.assertRaises(ResourceNotFoundException):
            self.ozza.get_member_by_field_value("a", "a", "a")
        with self.assertRaises(FieldNotFoundException):
            self.ozza.get_member_by_field_value("test-data", "test", "test")
        result1 = self.ozza.get_member_by_field_value("test-data", "name", "some-name")
        result2 = self.ozza.get_member_by_field_value("test-data", "name", "s*e")
        self.assertEqual(result1, result2)
        self.assertEqual(result1[0].get("name"), data.get("name"))

        data = dict(id="some-id2", name="some-name2")
        self.ozza.put_member("test-data", data, expiry=2)
        not_expired = self.ozza.get_member_by_field_value("test-data", "name", "some-name2")
        self.assertEqual(not_expired[0].get("id"), "some-id2")
        time.sleep(3)
        expired = self.ozza.get_member_by_field_value("test-data", "name", "some-name2")
        self.assertEqual(len(expired), 0)

    def test_delete_resource_by_key_id(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.delete_member(None, None)
        with self.assertRaises(ResourceNotFoundException):
            self.ozza.delete_member("some-key", "some-id")
        data = dict(id="some-id", name="some-name")
        self.ozza.put_member("test-data", data)
        result = self.ozza.delete_member("test-data", "some-id")
        self.assertEqual(result, "Delete successful")
        result = self.ozza.delete_member("test-data", "someid")
        self.assertEqual(result, "Member not found")

    def test_get_member_by_value(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.get_member_by_value(None, None)
        with self.assertRaises(ResourceNotFoundException):
            self.ozza.get_member_by_value("some-key", "some-id")
        data1 = dict(id="some-id1", name="some-name1")
        self.ozza.put_member("test-data", data1)
        data2 = dict(id="some-id2", name="some-name2")
        self.ozza.put_member("test-data", data2)
        data3 = dict(id="some-id3", name="some-name3")
        self.ozza.put_member("test-data", data3)
        data4 = dict(id="some-id4", name="some-name4")
        self.ozza.put_member("test-data", data4)
        data5 = dict(id="some-id5", name="some-name5")
        self.ozza.put_member("test-data", data5)
        data6 = dict(id="some-id6", name="some-name6")
        self.ozza.put_member("test-data", data6)
        result = self.ozza.get_member_by_value("test-data", "some-name5")
        self.assertEqual(result[0].get("name"), data5.get("name"))

    def test_member_id_existed(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.check_member(None, None)
        with self.assertRaises(ResourceNotFoundException):
            self.ozza.check_member("xyz", "abc")
        data1 = dict(id="some-id1", name="some-name1")
        self.ozza.put_member("test-data", data1)
        data2 = dict(id="some-id2", name="some-name2")
        self.ozza.put_member("test-data", data2)
        data3 = dict(id="some-id3", name="some-name3")
        self.ozza.put_member("test-data", data3)
        self.assertTrue(self.ozza.check_member("test-data", "some-id3"))
        self.assertFalse(self.ozza.check_member("test-data", "some-id"))

    def test_resource_is_available(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza._resource_is_available(None)
        self.ozza.create_resource("test-data")
        self.assertTrue(self.ozza._resource_is_available("test-data"))

    def test_field_is_available(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza._member_key_is_available(None, None)
        with self.assertRaises(ResourceNotFoundException):
            self.ozza._member_key_is_available("aa", "bb")
        data1 = dict(id="some-id1", name="some-name1")
        self.ozza.put_member("test-data", data1)
        self.assertTrue(self.ozza._member_key_is_available("test-data", "name"))

    def test_matching_resource(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza._fetch_matching_resource(None)
        data1 = dict(id="some-id1", name="some-name1")
        self.ozza.put_member("test-data", data1)
        result = self.ozza._fetch_matching_resource("t*a")
        self.assertEqual(result[0].get("name"), data1.get("name"))

    def test_multiple_filters(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.multiple_filter_member(None, None)
        with self.assertRaises(EmptyParameterException):
            self.ozza.multiple_filter_member(None, None, condition="or")
        with self.assertRaises(ResourceNotFoundException):
            self.ozza.multiple_filter_member("test_data", [{"id": "1"}])
        with self.assertRaises(ResourceNotFoundException):
            self.ozza.multiple_filter_member("test_data", [{"id": "1"}], condition="or")
        self.ozza.put_member("test-data", dict(id="some-id", name="some-name", email="some-email", phone="somephone"))
        self.ozza.put_member("test-data", dict(id="some-id2", name="some-name", email="some-email2", phone="somephone"))
        with self.assertRaises(InvalidFilterFormatException):
            self.ozza.multiple_filter_member("test-data", [{"field_name": "email", "field_value": "some-email"}])
        with self.assertRaises(InvalidFilterFormatException):
            self.ozza.multiple_filter_member("test-data", [{"field": "email_address", "value": "some-email"}])
        with self.assertRaises(InvalidFilterFormatException):
            self.ozza.multiple_filter_member("test-data", [{"field_name": "email", "field_value": "some-email"}],
                                             condition="or")
        with self.assertRaises(InvalidFilterFormatException):
            self.ozza.multiple_filter_member("test-data", [{"field": "email_address", "value": "some-email"}],
                                             condition="or")
        filters = [{"field": "phone", "value": "somephon"}, {"field": "name", "value": "some-name"}]
        result_and = self.ozza.multiple_filter_member("test-data", filters, condition="and")
        self.assertEqual(len(result_and), 0)
        result_or = self.ozza.multiple_filter_member("test-data", filters, condition="or")
        self.assertEqual(len(result_or), 2)

    def test_put_value(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.put_value(None, None)
        data = self.ozza.put_value("value-test", "some-value")
        test_value = self.ozza.get_resource("value-test")
        self.assertEqual(data, test_value)


    def tearDown(self):
        self.ozza._teardown_data()
