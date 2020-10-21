import unittest
import time
import os

from json.decoder import JSONDecodeError
from exceptions import *
from ozza import Ozza


class OzzaTest(unittest.TestCase):

    def setUp(self):
        self.ozza = Ozza(test_mode=True)

    def test_creation(self):
        self.assertEqual(self.ozza._in_memory_data, {})

    def test_json_decode_error(self):
        os.environ["DATA_DIRECTORY"] = "test/"
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
        self.assertTrue(data in resource_set[0])
        resource_set = self.ozza.get("t$t")
        self.assertTrue(data in resource_set[0])

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
        not_expired = self.ozza.get_resource_by_field_value("test-data","name","some-name2")
        self.assertEqual(not_expired[0].get("id"), "some-id2")
        time.sleep(3)
        expired = self.ozza.get_resource_by_field_value("test-data","name","some-name2")
        self.assertEqual(len(expired), 0)

    def test_delete_resource_by_key_id(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.delete_resource_by_id(None, None)
        with self.assertRaises(ResourceGroupNotFoundException):
            self.ozza.delete_resource_by_id("some-key","some-id")
        data = dict(id="some-id", name="some-name")
        self.ozza.add_data("test-data", data)
        result = self.ozza.delete_resource_by_id("test-data","some-id")
        self.assertEqual(result, "Delete successful")


    def tearDown(self):
        self.ozza._teardown_data()
