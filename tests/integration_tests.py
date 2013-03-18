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
        client = smk_api.login(adapter_context.TEST_SMK_LOGIN, adapter_context.TEST_SMK_PASSWORD).result
        client.logout()
        
    def test_that_smk_api_thows_SocketDisconnected_exception_if_credentials_are_wrong(self):
        #using different login to avoid user blocking
        self.assertFalse(smk_api.login('wrongLogin_' + str(time.time()), 'wrongPassword').succeeded)
    
    def test_bet_placing_workflow(self):
        client = smk_api.login(adapter_context.TEST_SMK_LOGIN, adapter_context.TEST_SMK_PASSWORD).result
        try:
            initialAmountOfMarkets = len(client.getBetsForAccount().bets)
            
            events = client.footballByDate(datetime.date.today())
            event = events.parentToEvent.values()[0][0]
            market = None
            if events.parentToEvent.get(str(event.eventId)) is None:
                market = event
            else: 
                market = events.parentToEvent[str(event.eventId)][0]
            self.assertFalse(market is None)
            
            
            contract = events.marketToContract.get(str(market.eventId))[0]
            self.assertFalse(contract is None)
            
            accountState = str(client.getAccountState())
            self.assertEqual(accountState, "AccountState(id=13700964455177639, currency=GBP, cash=10.0, bonus=0.0, exposure=0.0)")
            
            bet = client.placeBet(market.eventId, contract.marketId, 22, 2400).result
            print "======>Bet: "+str(bet)
            self.assertEqual(initialAmountOfMarkets+1, len(client.getBetsForAccount().bets))
            cancelBetResponse = client.cancelBet(bet.id).result
            self.assertEqual(initialAmountOfMarkets, len(client.getBetsForAccount().bets))
            print "======>CancelBet: "+str(cancelBetResponse)
            
        finally:
            client.logout()
