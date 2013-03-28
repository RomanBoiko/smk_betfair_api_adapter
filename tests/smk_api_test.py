import unittest
import time
import datetime
import urllib2
import os

from smarkets.exceptions import SocketDisconnected
import smarkets
import smarkets.uuid
from smarkets.uuid import Uuid, uuid_to_int
from smarkets.clients import Smarkets

import smkadapter.adapter_context as adapter_context
import smkadapter.smk_api as smk_api

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

    def test_that_order_status_convertion_is_correct(self):
        self.assertEqual(smk_api.smkOrderStatusCodeToString(1), "LIVE")
        self.assertEqual(smk_api.smkOrderStatusCodeToString(2), "PARTIALLY_FILLED")
        self.assertEqual(smk_api.smkOrderStatusCodeToString(3), "FILLED")
        self.assertEqual(smk_api.smkOrderStatusCodeToString(4), "PARTIALLY_CANCELLED")
        self.assertEqual(smk_api.smkOrderStatusCodeToString(5), "CANCELLED")

    def test_that_smk_order_status_converts_correctly_to_betfair_status(self):
        self.assertEqual(smk_api.smkOrderStatusToBetfairBetStatus(1), "U")#Unmatched
        self.assertEqual(smk_api.smkOrderStatusToBetfairBetStatus(2), "MU")#Matched and Unmatched
        self.assertEqual(smk_api.smkOrderStatusToBetfairBetStatus(3), "M")#Matched
        self.assertEqual(smk_api.smkOrderStatusToBetfairBetStatus(4), "M")#Matched? or better Settled or Voided?
        self.assertEqual(smk_api.smkOrderStatusToBetfairBetStatus(5), "C")#Cancelled

    def eventsPayloadFromFile(self, pathToFile):
        fileStream = urllib2.urlopen("file://%s"%os.path.abspath(pathToFile))
        data = fileStream.read()
        fileStream.close()
        
        incoming_payload = seto.Events()
        incoming_payload.ParseFromString(data)
        return incoming_payload

    PARENTS_IN_FILE_1 = 90
    EVENTS_AND_MARKETS_IN_FILE_1 = 3702
    MARKETS_IN_FILE_1 = 3613
    CONTRACTS_IN_FILE_1 = 7478

    PARENTS_IN_FILE_2 = 43
    EVENTS_AND_MARKETS_IN_FILE_2 = 1564
    MARKETS_IN_FILE_2 = 1522
    CONTRACTS_IN_FILE_2 = 3132

    def test_that_events_file_1_can_be_loaded_separately(self):
        incoming_payload = self.eventsPayloadFromFile("tests/resources/events_day_1.pb")
        events = smk_api.EventsParser().parseEvents([incoming_payload])

        self.assertEqual(events.parentsCount(), self.__class__.PARENTS_IN_FILE_1)
        self.assertEqual(events.eventsAndMarketsCount(), self.__class__.EVENTS_AND_MARKETS_IN_FILE_1)
        self.assertEqual(events.marketsCount(), self.__class__.MARKETS_IN_FILE_1)
        self.assertEqual(events.contractsCount(), self.__class__.CONTRACTS_IN_FILE_1)

    def test_that_events_file_2_can_be_loaded_separately(self):
        incoming_payload = self.eventsPayloadFromFile("tests/resources/events_day_2.pb")
        events = smk_api.EventsParser().parseEvents([incoming_payload])

        self.assertEqual(events.parentsCount(), self.__class__.PARENTS_IN_FILE_2)
        self.assertEqual(events.eventsAndMarketsCount(), self.__class__.EVENTS_AND_MARKETS_IN_FILE_2)
        self.assertEqual(events.marketsCount(), self.__class__.MARKETS_IN_FILE_2)
        self.assertEqual(events.contractsCount(), self.__class__.CONTRACTS_IN_FILE_2)

    def test_that_events_from_both_files_could_be_loaded_and_merged(self):
        incomingPayload1 = self.eventsPayloadFromFile("tests/resources/events_day_1.pb")
        incomingPayload2 = self.eventsPayloadFromFile("tests/resources/events_day_2.pb")
        events = smk_api.EventsParser().parseEvents([incomingPayload1, incomingPayload2])
        
        self.assertEqual(events.eventsAndMarketsCount(), self.__class__.EVENTS_AND_MARKETS_IN_FILE_1 + self.__class__.EVENTS_AND_MARKETS_IN_FILE_2)
        self.assertEqual(events.marketsCount(), self.__class__.MARKETS_IN_FILE_1 + self.__class__.MARKETS_IN_FILE_2)
        self.assertEqual(events.contractsCount(), self.__class__.CONTRACTS_IN_FILE_1 + self.__class__.CONTRACTS_IN_FILE_2)


