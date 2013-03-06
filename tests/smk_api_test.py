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


class SmkApiUnitTest(unittest.TestCase):
    def test_that_uuid_arithmetic_works_as_expected(self):
        uu = Uuid.from_int((0, 282382), 'Account')
        print "===> %s"%uu.to_hex()
        print "===> %s"%str(uuid_to_int(uu.to_hex()))
        print "===> %s"%Smarkets.str_to_uuid128(uu.to_hex())
