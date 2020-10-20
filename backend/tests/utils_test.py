import unittest

from utils import *


class UtilsTest(unittest.TestCase):

    def test_get_unix_milis(self):
        checker = 1603225220000
        test_time = datetime(2020, 10, 20, 20, 20, 20)
        milistime = get_unix_millis(test_time)
        self.assertEqual(milistime, checker)

    def test_get_expiry_time(self):
        checker = 1603225230000
        expiry_in_seconds = 10
        test_time = datetime(2020, 10, 20, 20, 20, 20)
        expiry_time = get_expiry_time(expiry_in_seconds, test_time)
        print(expiry_time)
        self.assertEqual(expiry_time, checker)
