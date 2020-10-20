import unittest

from ozza import Ozza
from exceptions import *


class OzzaTest(unittest.TestCase):

    def setUp(self):
        self.ozza = Ozza(test_mode=True)

    def test_creation(self):
        self.assertEqual(self.ozza._in_memory_data, {})

    def test_create_resource(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.create_resource(None)

        self.ozza.create_resource("test-data")
        self.assertTrue("test-data" in self.ozza._in_memory_data)


    def test_add_data(self):
        with self.assertRaises(EmptyParameterException):
            self.ozza.add_data(None,None)

        with self.assertRaises(IdNotFoundException):
            data = dict(name="some-name")
            self.ozza.add_data("test-set", data)

        data = dict(id="some-id",name="some-name")
        self.ozza.add_data("test-set", data)
        resource_set = self.ozza.get("test-set")
        self.assertTrue(data in resource_set[0])
        resource_set = self.ozza.get("t$t")
        self.assertTrue(data in resource_set[0])

    def test_update_resource(self):
        self.ozza.create_resource("test-data")
        with self.assertRaises(EmptyParameterException):
            self.ozza.update_resource(None,None,None)
        with self.assertRaises(ResourceGroupNotFoundException):
            self.ozza.update_resource("a-key","haha",{"key":"value"})
        with self.assertRaises(IdNotFoundException):
            self.ozza.update_resource("test-data", "haha",{"key":"value"})
        with self.assertRaises(MismatchIdException):
            self.ozza.update_resource("test-data", "haha",{"id":"hah","key":"value"})
        data = dict(id="some-id", name="some-name")
        self.ozza.add_data("test-data", data)
        data["name"] = "some-updated-name"
        result = self.ozza.update_resource("test-data","some-id", data)
        self.assertEqual(data.get("name"), result.get("name"))

    def test_delete_value_from_resource(self):
        data = dict(id="some-id", name="some-name")
        self.ozza.add_data("test-data", data)
        data = dict(id="some-id2", name="some-name")
        self.ozza.add_data("test-data", data)
        self.ozza.delete_value_from_resource("test-data","some-id")
        result = self.ozza.get_resource_by_id("test-data", "some-id")
        self.assertEqual(result,[])

    def test_delete_resource(self):
        self.ozza.create_resource("test-data")
        with self.assertRaises(EmptyParameterException):
            self.ozza.delete_resource(None)
        with self.assertRaises(ResourceGroupNotFoundException):
            self.ozza.delete_resource("not found")
        self.ozza.delete_resource("test-data")
        self.assertEqual(self.ozza.get("test-data"), [])

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
        print(result1)
        self.assertEqual(result1[0].get("name"), data.get("name"))


    def tearDown(self):
        self.ozza._teardown_data()
