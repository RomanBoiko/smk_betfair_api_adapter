from __future__ import unicode_literals

import sys
import unittest
import time

from mock import patch, Mock
from lxml import etree
import datetime

import logging

sys.path.append('dependencies/bfpy/src')
import bfpy
import bfpy.bfclient as bfclient
import bfpy.bfprocessors
from bfpy.bferror import BfError

from smkadapter import smk_api,betfair_api, adapter, adapter_context

SOAP_ENVELOPE = """<?xml version="1.0"?>
                    <soapenv:Envelope 
                            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                            xmlns:bfg="http://www.betfair.com/publicapi/v3/BFGlobalService/"
                            xmlns:bfex="http://www.betfair.com/publicapi/v5/BFExchangeService/"
                            xmlns:v5="http://www.betfair.com/publicapi/types/exchange/v5/">
                       <soapenv:Header/>
                       <soapenv:Body>%s</soapenv:Body>
                    </soapenv:Envelope>
                """

loginRequest = """<bfg:login>
                       <bfg:request>
                           <ipAddress>0</ipAddress>
                           <locationId>0</locationId>
                           <password>password</password>
                           <productId>82</productId>
                           <username>username</username>
                           <vendorSoftwareId>0</vendorSoftwareId>
                       </bfg:request>
                   </bfg:login>"""

SESSION_TOKEN="someSessionToken"
LOG = logging.getLogger('[betfair.api.test]')

def xmlElement(xml, elementName):
    return etree.XML(str(xml)).xpath("//*[local-name()='%s']"%elementName)

def mockGetAccountFundsResponse(businessUnitMock):
    accountFundsResponseMock = businessUnitMock.getAccountFunds.return_value
    accountFundsResponseMock.currency="GBP"
    accountFundsResponseMock.cash=1111.0
    accountFundsResponseMock.exposure=222.0
    
def mockSuccessfulLoginResponse(businessUnitMock):
    businessUnitMock.authenticateUserAndReturnHisSessionToken.return_value = smk_api.ActionSucceeded(SESSION_TOKEN)
    

class BetfairApiUnitTest(unittest.TestCase):
    @patch('smkadapter.betfair_api.businessUnit')
    def test_login_action_to_be_dispatched_and_to_return_session_token(self, BusinessUnitMock):
        businessUnitMock = BusinessUnitMock.return_value
        mockSuccessfulLoginResponse(businessUnitMock)
        mockGetAccountFundsResponse(businessUnitMock)

        result = betfair_api.dispatchRequest(SOAP_ENVELOPE%loginRequest)

        LOG.debug("login result: %s"%result)
        businessUnitMock.authenticateUserAndReturnHisSessionToken.assert_called_with("username", "password")
        self.assertEqual(xmlElement(result, "sessionToken")[0].text, SESSION_TOKEN)

class SmkMarketPricesMock(object):
    def __init__(self, marketId, contracts):
        self.marketId = marketId
        self.contracts = contracts

class MarketPricesCompressionUnitTest(unittest.TestCase):
    def test_that_market_prices_are_compressing_fine(self):
        marketId = 123
        contractId = 333
        bids = [smk_api.MarketPrice(544, 2.34), smk_api.MarketPrice(541, 2.33)]
        offers = [smk_api.MarketPrice(12, 1.34)]
        contracts = [smk_api.ContractPrices(contractId, bids, offers),smk_api.ContractPrices(contractId+1, bids, offers)]
        smkMarketPrices = SmkMarketPricesMock(marketId, contracts)
        compressionResult = betfair_api.MarketPrices(smkMarketPrices).compress()
        self.assertEquals("123~GBP~ACTIVE~0~1~None~false~0.0~0~~N:333~0~0.0~0.0~~0.0~false~0.0~0.0~0.0|12~1.34~L~1|544~2.34~B~1~541~2.33~B~1:334~0~0.0~0.0~~0.0~false~0.0~0.0~0.0|12~1.34~L~1|544~2.34~B~1~541~2.33~B~1",
                          compressionResult)
        print str(bfpy.bfprocessors.ProcMarketPricesCompressed().ParseMarketPricesCompressed(compressionResult))

class BetfairApiIntegrationTest(unittest.TestCase):
    @patch('smkadapter.betfair_api.businessUnit')
    def test_flow_using_bfpy(self, BusinessUnitMock):
        businessUnitMock = BusinessUnitMock.return_value
        
        mockSuccessfulLoginResponse(businessUnitMock)
        mockGetAccountFundsResponse(businessUnitMock)
        
        adapter.startThread(adapter.betfairApiServer)
        LOG.info("sleeping to allow web-server to stop...")
        time.sleep(1)
        LOG.info("starting test")
        
        bfClient = self.should_login_and_return_bfpy_BfClient(businessUnitMock)
        self.should_access_account_funds(bfClient, businessUnitMock)
        self.should_access_event_types(bfClient, businessUnitMock)
        self.should_access_current_accounts_bets(bfClient, businessUnitMock)
        self.should_place_bets(bfClient, businessUnitMock)
        self.should_cancel_bets(bfClient, businessUnitMock)
        self.should_get_compressed_market_prices(bfClient, businessUnitMock)
        self.should_get_all_markets(bfClient, businessUnitMock)
        self.should_cancel_bets_by_market(bfClient, businessUnitMock)
        self.should_get_MUBets(bfClient, businessUnitMock)
        self.should_get_bet(bfClient, businessUnitMock)
        self.should_logout_from_session(bfClient, businessUnitMock)
        
    def should_login_and_return_bfpy_BfClient(self, businessUnitMock):
        bfClient = bfclient.BfClient()
        adapterResponse = bfClient.login(username=adapter_context.TEST_SMK_LOGIN, password=adapter_context.TEST_SMK_PASSWORD)
        LOG.debug(adapterResponse)
        businessUnitMock.authenticateUserAndReturnHisSessionToken.assert_called_with(adapter_context.TEST_SMK_LOGIN, adapter_context.TEST_SMK_PASSWORD)
        self.assertTrue('sessionToken = "%s"'%SESSION_TOKEN in str(adapterResponse))
        return bfClient
    
    def should_access_account_funds(self, bfClient, businessUnitMock):
        adapterResponse = str(bfClient.getAccountFunds(bfpy.ExchangeUK))
        LOG.debug(adapterResponse)
        self.assertTrue('balance = 1111.0' in adapterResponse)
        self.assertTrue('exposure = 222.0' in adapterResponse)
        

    def should_access_event_types(self, bfClient, businessUnitMock):
        adapterResponse = str(bfClient.getAllEventTypes())
        LOG.debug(adapterResponse)
        self.assertTrue('id = 125062' in adapterResponse)
        self.assertTrue('name = "Football"' in adapterResponse)
        
    def should_access_current_accounts_bets(self, bfClient, businessUnitMock):
        self.mockGetBetsForAccount(businessUnitMock)
        adapterResponse = str(bfClient.getCurrentBets(bfpy.ExchangeUK))
        LOG.debug(adapterResponse)
        businessUnitMock.getBetsForAccount.assert_called()
        self.assertTrue('betId = 123' in adapterResponse)
        self.assertTrue('betId = 124' in adapterResponse)
        
    def mockGetBetsForAccount(self, businessUnitMock):
        response = businessUnitMock.getBetsForAccount.return_value
        orderId=123
        marketId=234
        contractId=333
        price=400.0
        status=1
        quantity=244.0
        createdDateInMillis="somedate"
        response.bets=[]
        response.bets.append(smk_api.BetDetails(orderId, marketId, "marketName", contractId, "contractName", price, status, quantity, createdDateInMillis, True))
        response.bets.append(smk_api.BetDetails(orderId+1, marketId, "marketName", contractId, "contractName", price, status, quantity, createdDateInMillis, False))
        
    def should_place_bets(self, bfClient, businessUnitMock):
        betResult=Mock()
        betResult.id=123
        businessUnitMock.placeBet.return_value = smk_api.ActionSucceeded(betResult)
        placeBet = bfClient.createPlaceBets()
        placeBet.asianLineId = 0
        # Man City = 47999
        # Chelsea = 55190
        placeBet.selectionId = 200153
        placeBet.price = 500
        placeBet.size = 2.0
        placeBet.bspLiability = 0.0
        placeBet.betType = 'B'
        placeBet.betCategoryType = 'E'
        placeBet.betPersistenceType = 'NONE'
        # English Premier League Winner 2011/2012
        placeBet.marketId = 135615
        
        adapterResponse = str(bfClient.placeBets(bfpy.ExchangeUK, bets=[placeBet]))
        #print 'sleeping 5 seconds'
        #bet = response.betResults[0]
        LOG.debug(adapterResponse)
        self.assertTrue('betId = 123' in adapterResponse)
        businessUnitMock.placeBet.assert_called_with(SESSION_TOKEN, 135615, 200153, 2.0, 500, True)
        
    def should_cancel_bets(self, bfClient, businessUnitMock):
        betResult=Mock()
        betResult.id=231
        businessUnitMock.cancelBet.return_value = smk_api.ActionSucceeded(betResult)
        cancelBet = bfClient.createCancelBets()
        cancelBet.betId = 231
        adapterResponse = str(bfClient.cancelBets(bfpy.ExchangeUK, bets=[cancelBet]))
        LOG.debug(adapterResponse)
        self.assertTrue('betId = 231' in adapterResponse)
        businessUnitMock.cancelBet.assert_called_with(SESSION_TOKEN, 231)

    def should_get_compressed_market_prices(self, bfClient, businessUnitMock):
        marketPricesObject = Mock()
        marketPricesObject.marketId = 444
        marketPricesObject.bids = []
        marketPricesObject.offers = []
        marketPricesObject.bids.append(smk_api.MarketPrice(200, 23.2))
        marketPricesObject.offers.append(smk_api.MarketPrice(201, 23.3))
        businessUnitMock.getMarketPrices.return_value = smk_api.ActionSucceeded(marketPricesObject)
        adapterResponse = str(bfClient.getMarketPricesCompressed(bfpy.ExchangeUK, marketId=144))
        LOG.debug(adapterResponse)
        self.assertTrue('marketId = 444' in adapterResponse)
        
    def should_get_all_markets(self, bfClient, businessUnitMock):
        events = smk_api.Events()
        eventId=12
        eventName="someEvent"
        eventTypeId = 1
        events.putMarket(233, smk_api.Event(eventId, eventName, eventTypeId, datetime.datetime(2012, 12, 22)))
        businessUnitMock.getTodaysFootballEvents.return_value = events
        adapterResponse = str(bfClient.getAllMarkets(bfpy.ExchangeUK))
        LOG.debug(adapterResponse)
#        self.assertTrue('marketId = 444' in adapterResponse)

    def should_logout_from_session(self, bfClient, businessUnitMock):
        adapterResponse = str(bfClient.logout())
        LOG.debug(adapterResponse)
        businessUnitMock.logUserOutAndReturnResultOfAction.assert_called_with(SESSION_TOKEN)
        self.assertTrue('errorCode = "OK"' in adapterResponse)
        
    def should_cancel_bets_by_market(self, bfClient, businessUnitMock):
        adapterResponse = str(bfClient.cancelBetsByMarket(bfpy.ExchangeUK, markets=[135615]))
        LOG.debug(adapterResponse)
        self.assertTrue('errorCode = "OK"' in adapterResponse)
        self.assertTrue('marketId = 135615' in adapterResponse)

    def should_get_MUBets(self, bfClient, businessUnitMock):
        adapterResponse = str(bfClient.getMUBets(bfpy.ExchangeUK, marketId=135615, betStatus='MU'))
        LOG.debug(adapterResponse)
        self.assertTrue('errorCode = "OK"' in adapterResponse)

    def should_get_bet(self, bfClient, businessUnitMock):
        self.mockGetBetsForAccount(businessUnitMock)
        adapterResponse = str(bfClient.getBet(bfpy.ExchangeUK, betId=123))
        LOG.debug(adapterResponse)
        self.assertTrue('errorCode = "OK"' in adapterResponse)
        self.assertTrue('remainingSize = 0.0244' in adapterResponse)


