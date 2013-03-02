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


class SmkApiIntegrationTest(unittest.TestCase):

    def test_that_smk_api_must_login_and_logout_successfuly(self):
        client = smk_api.login(adapter_context.TEST_SMK_LOGIN, adapter_context.TEST_SMK_PASSWORD)
        smk_api.logout(client)
        
    def test_that_smk_api_thows_SocketDisconnected_exception_if_credentials_are_wrong(self):
        try:
            #using different login to avoid user blocking
            smk_api.login('wrongLogin_' + str(time.time()), 'wrongPassword')
        except SocketDisconnected:
            assert True
        else:
            assert False
            
    def test_that_uuid_arithmetic_works_like_expected(self):
#        client = smk_api.login(adapter_context.TEST_SMK_LOGIN, adapter_context.TEST_SMK_PASSWORD)
#        smk_api.EventsBroker().getEvents(client, smarkets.events.FootballByDate(datetime.date(2013, 3, 2)))
#        smk_api.SmkBroker(client).getAccountState()
#        smk_api.SmkBroker(client).getBetsForAccount()
#        smk_api.logout(client)
        uu = Uuid.from_int((0, 282382), 'Account')
        print "===> %s"%uu.to_hex()
        print "===> %s"%str(uuid_to_int(uu.to_hex()))
        print "===> %s"%Smarkets.str_to_uuid128(uu.to_hex())
        
