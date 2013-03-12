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
        client.logout()
        
    def test_that_smk_api_thows_SocketDisconnected_exception_if_credentials_are_wrong(self):
        try:
            #using different login to avoid user blocking
            smk_api.login('wrongLogin_' + str(time.time()), 'wrongPassword')
        except SocketDisconnected:
            assert True
        else:
            assert False
    
    def test_bet_placing_workflow(self):
        client = smk_api.login(adapter_context.TEST_SMK_LOGIN, adapter_context.TEST_SMK_PASSWORD)
        try:
            eventsBroker = smk_api.EventsBroker(client)
            events = eventsBroker.footballByDate(datetime.date(2013, 3, 11))
            event = events.parentToEvent.values()[0][0]
            market = None
            if events.parentToEvent.get(str(event.eventId)) is None:
                market = event
            else: 
                market = events.parentToEvent[str(event.eventId)][0]
            self.assertFalse(market is None)
            
            contract = events.marketToContract.get(str(market.eventId))[0]
            self.assertFalse(contract is None)
            
            self.makeSureAccountIsInInitialStateAndHasNoActiveBets(client)
            
            bet = client.placeBet(market.eventId, contract.marketId, 220000, 2400)
            print "======>Bet: "+str(bet)
            self.assertEqual(1, len(client.getBetsForAccount().markets))
            cancelBetResponse = client.cancelBet(bet.id)
            print "======>CancelBet: "+str(cancelBetResponse)
            
            self.makeSureAccountIsInInitialStateAndHasNoActiveBets(client)
            
        finally:
            client.logout()
            
    def makeSureAccountIsInInitialStateAndHasNoActiveBets(self, client):
        self.assertEqual(str(client.getAccountState()), "AccountState(id=13700964455177639, currency=1, cash=100000, bonus=0, exposure=0)")
        self.assertEqual(0, len(client.getBetsForAccount().markets))