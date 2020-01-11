import unittest
import win32api

from logs.Logging import *
from environmental_testing.check_internet_connection import *


class MyTest(unittest.TestCase):
    def test(self):
        try:
            self.assertEqual(is_connected(), True)
            logger.info('Internet connection exists')
        except:
            logger.info('Internet connection failed')
            win32api.MessageBox(0, 'Internet connection failed')