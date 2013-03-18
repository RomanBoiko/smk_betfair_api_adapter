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

TEST_TAG = 'Account'

class SmkApiUnitTest(unittest.TestCase):
    def assertUuidsConversionIsSymmetric(self, originalUuid):
        uuidAfterSymmetricConvertion = smk_api.integerToUuid(smk_api.uuidToInteger(originalUuid))
        self.assertEqual(uuidAfterSymmetricConvertion.low, originalUuid.low)
        self.assertEqual(uuidAfterSymmetricConvertion.high, originalUuid.high)
        
    def test_that_uuidToInteger_and_integerToUuid_are_symmetric(self):
        testId=1231
        uid = Uuid.from_int(testId, TEST_TAG)
        
        self.assertUuidsConversionIsSymmetric(uid)
        
    def test_that_uuidToInteger_and_integerToUuid_are_symmetric_with_low_and_high(self):
        uid = Uuid.from_int((ORIGINAL_HIGH, ORIGINAL_LOW), TEST_TAG)
        
        self.assertUuidsConversionIsSymmetric(uid)
        
    def test_that_uuidToInteger_and_integerToUuid_are_symmetric_with_low_and_high_if_high_is_zero(self):
        uid = Uuid.from_int((0, ORIGINAL_LOW), TEST_TAG)

        self.assertUuidsConversionIsSymmetric(uid)

    def test_that_currency_convertion_works(self):
        self.assertEqual(smk_api.extractCurrencyFromAccountStateMessage(1), "GBP")
        self.assertEqual(smk_api.extractCurrencyFromAccountStateMessage(2), "EUR")
