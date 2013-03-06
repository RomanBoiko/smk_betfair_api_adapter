import unittest
import time
import datetime

from smarkets.exceptions import SocketDisconnected
import smarkets
import smarkets.uuid
from smarkets.uuid import Uuid, uuid_to_int
from smarkets.clients import Smarkets

import adapter_context
import smk_api

import smarkets.seto.piqi_pb2 as seto

ORIGINAL_LOW = 282382
ORIGINAL_HIGH = 234

class SmkApiUnitTest(unittest.TestCase):

    def test_that_uuid_arithmetic_with_low_works_as_expected(self):
        uid = Uuid.from_int((0, ORIGINAL_LOW), 'Account')
        self.assertEqual(ORIGINAL_LOW, uuid_to_int(uid.to_hex()))
        self.assertEqual(ORIGINAL_LOW, Smarkets.str_to_uuid128(uid.to_hex()).low)
        
    def test_that_uuid_arithmetic_with_low_and_high_works_as_expected(self):
        uid = Uuid.from_int((ORIGINAL_HIGH, ORIGINAL_LOW), 'Account')
        
        self.assertTrue(isinstance( uuid_to_int(uid.to_hex()), ( int, long ) ) )
        
        self.assertEqual(ORIGINAL_LOW, Smarkets.str_to_uuid128(uid.to_hex()).low)
        self.assertEqual(ORIGINAL_HIGH, Smarkets.str_to_uuid128(uid.to_hex()).high)
        
    def test_that_uuid_arithmetic_with_low_and_high_with_high_as_zero(self):
        uid = Uuid.from_int((0, ORIGINAL_LOW), 'Account')
        self.assertEqual(uuid_to_int(uid.to_hex()), ORIGINAL_LOW )

    def test_that_uuid_arithmetic_with_int_works_as_expected(self):
        testId=1231
        uid = Uuid.from_int(testId, 'Account')
        self.assertEqual(testId, uuid_to_int(uid.to_hex()))
        