import sys
import unittest
import time

from mock import patch
from lxml import etree

import logging

sys.path.append('dependencies/bfpy/src')
import bfpy
import bfpy.bfclient as bfclient
from bfpy.bferror import BfError

from smkadapter import smk_api,betfair_api_nozsi, adapter, adapter_context

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
    return etree.XML(betfair_api_nozsi.unicodeXml(xml)).xpath("//*[local-name()='%s']"%elementName)

def mockGetAccountFundsResponse(businessUnitMock):
    accountFundsResponseMock = businessUnitMock.getAccountFunds.return_value
    accountFundsResponseMock.currency="GBP"    accountFundsResponseMock.cash=1111.00    accountFundsResponseMock.exposure=222.00
    
def mockSuccessfulLoginResponse(businessUnitMock):
    businessUnitMock.authenticateUserAndReturnHisSessionToken.return_value = smk_api.ActionSucceeded(SESSION_TOKEN)

class BetfairApiUnitTest(unittest.TestCase):
    @patch('smkadapter.betfair_api_nozsi.businessUnit')
    def test_login_action_to_return_session_token(self, BusinessUnitMock):
        businessUnitMock = BusinessUnitMock.return_value
        mockSuccessfulLoginResponse(businessUnitMock)
        mockGetAccountFundsResponse(businessUnitMock)

        result = betfair_api_nozsi.dispatchRequest(SOAP_ENVELOPE%loginRequest)

        LOG.debug("login result: %s"%result)
        businessUnitMock.authenticateUserAndReturnHisSessionToken.assert_called_with("username", "password")
        self.assertEqual(xmlElement(result, "sessionToken")[0].text, SESSION_TOKEN)

class BetfairApiIntegrationTest(unittest.TestCase):
    @patch('smkadapter.betfair_api_nozsi.businessUnit')
    def test_flow_using_bfpy(self, BusinessUnitMock):
        businessUnitMock = BusinessUnitMock.return_value
        
        mockSuccessfulLoginResponse(businessUnitMock)
        mockGetAccountFundsResponse(businessUnitMock)
        
        adapter.startThread(adapter.betfairApiServer)
        LOG.info("sleeping to allow web-server to stop...")
        time.sleep(1)
        LOG.info("starting test")
        run_business_flow()


def run_business_flow():
    bf = bfclient.BfClient()

    try:
        bfrespLogin = bf.login(username=adapter_context.TEST_SMK_LOGIN, password=adapter_context.TEST_SMK_PASSWORD)
        print bfrespLogin

        accountFundsResponse = bf.getAccountFunds(bfpy.ExchangeUK)
        print accountFundsResponse

        # bfrespEventTypes = bf.getAllEventTypes()
        # print bfrespEventTypes

        # currentBets = bf.getCurrentBets(bfpy.ExchangeUK)
        # print currentBets
        
        # self.placeBets(bf)

        bfLogout = bf.logout()
        print bfLogout
    except BfError, e:
        print "adapter error: %s" % str(e)
        raise

def placeBets(bf):
    placeBet = bf.createPlaceBets()

    placeBet.asianLineId = 0
    # Man City = 47999
    # Chelsea = 55190
    placeBet.selectionId = 200153
    placeBet.price = 500.0
    placeBet.size = 2.0
    placeBet.bspLiability = 0.0
    placeBet.betType = 'B'
    placeBet.betCategoryType = 'E'
    placeBet.betPersistenceType = 'NONE'
    # English Premier League Winner 2011/2012
    placeBet.marketId = 135615
    
    response = bf.placeBets(bfpy.ExchangeUK, bets=[placeBet])
    print response
#        print 'sleeping 5 seconds'
#        bet = response.betResults[0]

#class AdapterExternalAcceptanceTest(unittest.TestCase):
#    def test_adapter_flow(self):
#        run_business_flow()

