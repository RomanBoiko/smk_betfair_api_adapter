import unittest

from mock import patch
from lxml import etree

import logging
import bfpybot

from smkadapter import smk_api,betfair_api_nozsi, adapter

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


class BetfairApiUnitTest(unittest.TestCase):
    @patch('smkadapter.betfair_api_nozsi.businessUnit')
    def test_login_action_to_return_session_token(self, BusinessUnitMock):
        businessUnitMock = BusinessUnitMock.return_value
        businessUnitMock.authenticateUserAndReturnHisSessionToken.return_value = smk_api.ActionSucceeded(SESSION_TOKEN)
        businessUnitMock.getAccountFunds.return_value.currency="GBP"
        result = betfair_api_nozsi.dispatchRequest(SOAP_ENVELOPE%loginRequest)

        LOG.debug("login result: %s"%result)
        businessUnitMock.authenticateUserAndReturnHisSessionToken.assert_called_with("username", "password")
        self.assertEqual(xmlElement(result, "sessionToken")[0].text, SESSION_TOKEN)

class BetfairApiIntegrationTest(unittest.TestCase):
    @patch('smkadapter.betfair_api_nozsi.businessUnit')
    def test_flow_using_bfpy(self, BusinessUnitMock):
        businessUnitMock = BusinessUnitMock.return_value
        businessUnitMock.authenticateUserAndReturnHisSessionToken.return_value = smk_api.ActionSucceeded(SESSION_TOKEN)
        businessUnitMock.getAccountFunds.return_value.currency="GBP"
        adapter.startThread(adapter.betfairApiServer)
        bfpybot.run_business_flow()