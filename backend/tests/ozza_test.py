import os
import time
import unittest

from exceptions import *
from ozza import Ozza


class OzzaTest(unittest.TestCase):

    def setUp(self):
        self.ozza = Ozza(test_mode=True)

    def test_creation(self):
        self.assertEqual(self.ozza._in_memory_data, {})

    def test_json_decode_error(self):
        os.environ["DATA_DIRECTORY"] = "tests/"
        os.environ["DATA_FILENAME"] = "brokenjson.oz"
        db = Ozza()
        self.assertEqual(db._in_memory_data, {})

    def test_create_resource(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.create_resource(None)

        self.ozza.create_resource("test-data")
        self.assertTrue("test-data" in self.ozza._in_memory_data)

    def test_add_data(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.add_data(None, None)

        with self.assertRaises(IdNotFoundException):
            data = dict(name="some-name")
            self.ozza.add_data("test-set", data)

        data = dict(id="some-id", name="some-name")
        self.ozza.add_data("test-set", data)
        resource_set = self.ozza.get("test-set")
        self.assertEqual(resource_set[0].get("name"), data.get("name"))
        resource_set = self.ozza.get("t$t")
        self.assertEqual(resource_set[0].get("name"), data.get("name"))
        data = dict(id="some-id", name="some-name2")
        self.ozza.add_data("test-set", data)
        self.assertEqual(resource_set[0].get("name"), data.get("name"))

    def test_update_resource(self):
        self.ozza.create_resource("test-data")
        with self.assertRaises(EmptyParameterException):
            self.ozza.update_resource(None, None, None)
        with self.assertRaises(ResourceGroupNotFoundException):
            self.ozza.update_resource("a-key", "haha", {"key": "value"})
        with self.assertRaises(IdNotFoundException):
            self.ozza.update_resource("test-data", "haha", {"key": "value"})
        with self.assertRaises(MismatchIdException):
            self.ozza.update_resource("test-data", "haha", {"id": "hah", "key": "value"})
        data = dict(id="some-id", name="some-name")
        self.ozza.add_data("test-data", data)
        data["name"] = "some-updated-name"
        result = self.ozza.update_resource("test-data", "some-id", data)
        self.assertEqual(data.get("name"), result.get("name"))

    def test_delete_value_from_resource(self):
        data = dict(id="some-id", name="some-name")
        self.ozza.add_data("test-data", data)
        data = dict(id="some-id2", name="some-name")
        self.ozza.add_data("test-data", data)
        self.ozza.delete_value_from_resource("test-data", "some-id")
        result = self.ozza.get_resource_by_id("test-data", "some-id")
        self.assertEqual(result, [])

    def test_delete_resource(self):
        self.ozza.create_resource("test-data")
        with self.assertRaises(EmptyParameterException):
            self.ozza.delete_resource(None)
        with self.assertRaises(ResourceGroupNotFoundException):
            self.ozza.delete_resource("not found")
        result = self.ozza.delete_resource("test-data")
        self.assertEqual(result, "Resource deleted")

    def test_get_resource_by_field_value(self):
        data = dict(id="some-id", name="some-name")
        self.ozza.add_data("test-data", data)
        with self.assertRaises(EmptyParameterException):
            self.ozza.get_resource_by_field_value(None, None, None)
        with self.assertRaises(ResourceGroupNotFoundException):
            self.ozza.get_resource_by_field_value("a", "a", "a")
        with self.assertRaises(FieldNotFoundException):
            self.ozza.get_resource_by_field_value("test-data", "test", "test")
        result1 = self.ozza.get_resource_by_field_value("test-data", "name", "some-name")
        result2 = self.ozza.get_resource_by_field_value("test-data", "name", "s$e")
        self.assertEqual(result1, result2)
        self.assertEqual(result1[0].get("name"), data.get("name"))

        data = dict(id="some-id2", name="some-name2")
        self.ozza.add_data("test-data", data, expiry=2)
        not_expired = self.ozza.get_resource_by_field_value("test-data", "name", "some-name2")
        self.assertEqual(not_expired[0].get("id"), "some-id2")
        time.sleep(3)
        expired = self.ozza.get_resource_by_field_value("test-data", "name", "some-name2")
        self.assertEqual(len(expired), 0)

    def test_delete_resource_by_key_id(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.delete_resource_by_id(None, None)
        with self.assertRaises(ResourceGroupNotFoundException):
            self.ozza.delete_resource_by_id("some-key", "some-id")
        data = dict(id="some-id", name="some-name")
        self.ozza.add_data("test-data", data)
        result = self.ozza.delete_resource_by_id("test-data", "some-id")
        self.assertEqual(result, "Delete successful")
        result = self.ozza.delete_resource_by_id("test-data", "someid")
        self.assertEqual(result, "Member not found")

    def test_get_member_by_value(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.get_member_by_value(None, None)
        with self.assertRaises(ResourceGroupNotFoundException):
            self.ozza.get_member_by_value("some-key", "some-id")
        data1 = dict(id="some-id1", name="some-name1")
        self.ozza.add_data("test-data", data1)
        data2 = dict(id="some-id2", name="some-name2")
        self.ozza.add_data("test-data", data2)
        data3 = dict(id="some-id3", name="some-name3")
        self.ozza.add_data("test-data", data3)
        data4 = dict(id="some-id4", name="some-name4")
        self.ozza.add_data("test-data", data4)
        data5 = dict(id="some-id5", name="some-name5")
        self.ozza.add_data("test-data", data5)
        data6 = dict(id="some-id6", name="some-name6")
        self.ozza.add_data("test-data", data6)
        result = self.ozza.get_member_by_value("test-data", "some-name5")
        self.assertEqual(result[0].get("name"), data5.get("name"))

    def test_member_id_existed(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.member_id_existed(None, None)
        with self.assertRaises(ResourceGroupNotFoundException):
            self.ozza.member_id_existed("xyz", "abc")
        data1 = dict(id="some-id1", name="some-name1")
        self.ozza.add_data("test-data", data1)
        data2 = dict(id="some-id2", name="some-name2")
        self.ozza.add_data("test-data", data2)
        data3 = dict(id="some-id3", name="some-name3")
        self.ozza.add_data("test-data", data3)
        self.assertTrue(self.ozza.member_id_existed("test-data", "some-id3"))
        self.assertFalse(self.ozza.member_id_existed("test-data", "some-id"))

    def test_resource_is_available(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza._resource_is_available(None)
        self.ozza.create_resource("test-data")
        self.assertTrue(self.ozza._resource_is_available("test-data"))

    def test_field_is_available(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza._field_is_available(None, None)
        with self.assertRaises(ResourceGroupNotFoundException):
            self.ozza._field_is_available("aa", "bb")
        data1 = dict(id="some-id1", name="some-name1")
        self.ozza.add_data("test-data", data1)
        self.assertTrue(self.ozza._field_is_available("test-data", "name"))

    def test_matching_resource(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza._fetch_matching_resources(None)
        data1 = dict(id="some-id1", name="some-name1")
        self.ozza.add_data("test-data", data1)
        result = self.ozza._fetch_matching_resources("t$a")
        self.assertEqual(result[0].get("name"), data1.get("name"))

    def tearDown(self):
        self.ozza._teardown_data()
