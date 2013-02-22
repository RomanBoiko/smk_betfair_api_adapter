import unittest

import httplib
from xml.dom.minidom import parseString

import betfair_api
import adapter_context
import time
from business_layer import SessionStorage

HOST="localhost"
PORT=int(adapter_context.BETFAIR_API_PORT)
BETFAIR_SERVICE = "/BFGlobalService"

ERROR_CODE_TAG="errorCode"
SESSION_TOKEN_TAG="sessionToken"


class SessionManagementAcceptanceTest(unittest.TestCase):

    def test_that_valid_credentials_are_causing_successful_login(self):
        responseDom = self.getLoginResponseDom(adapter_context.TEST_SMK_PASSWORD, adapter_context.TEST_SMK_LOGIN)
        
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_CODE_OK)
        sessionToken = self.sessionTokenFrom(responseDom)
        self.assertEquals(len(sessionToken), SessionStorage.SESSION_TOKEN_LENGTH)

        self.getLogoutResponseDom(sessionToken)

    def test_that_invalid_credentials_are_causing_login_failure(self):
        responseDom = self.getLoginResponseDom('wrongLogin_' + str(time.time()), 'wrongPassword')
        
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_INVALID_USERNAME_OR_PASSWORD)
        self.assertEquals(responseDom.getElementsByTagName(SESSION_TOKEN_TAG)[0].firstChild, None)

    def test_that_logout_with_nonexisting_session_token_results_unsuccessfuly(self):
        responseDom = self.getLogoutResponseDom("invalidSessionToken")
        #THEN
        self.assertErrorCodeInHeaderIs(responseDom, betfair_api.ERROR_NO_SESSION)
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_API_ERROR)

    def test_that_logout_with_valid_session_token_results_successfuly(self):
        loginResponseDom = self.getLoginResponseDom(adapter_context.TEST_SMK_PASSWORD, adapter_context.TEST_SMK_LOGIN)
        validSessionToken = self.sessionTokenFrom(loginResponseDom)
        logoutResponseDom = self.getLogoutResponseDom(validSessionToken)
        #THEN
        self.assertErrorCodeInHeaderIs(logoutResponseDom, betfair_api.ERROR_CODE_OK)
        self.assertResultErrorCodeIs(logoutResponseDom, betfair_api.ERROR_CODE_OK)
        
    def assertErrorCodeInHeaderIs(self, response, expectedErrorCode):
        self.assertEquals(textFromElement(response, ERROR_CODE_TAG, 0), expectedErrorCode)
    def assertResultErrorCodeIs(self, response, expectedErrorCode):
        self.assertEquals(textFromElement(response, ERROR_CODE_TAG, 1), expectedErrorCode)
    def sessionTokenFrom(self, response):
        return textFromElement(response, SESSION_TOKEN_TAG, 0)

    loginRequest = """<bfg:login>
                         <bfg:request>
                            <ipAddress>0</ipAddress>
                            <locationId>0</locationId>
                            <password>%s</password>
                            <productId>82</productId>
                            <username>%s</username>
                            <vendorSoftwareId>0</vendorSoftwareId>
                         </bfg:request>
                      </bfg:login>"""

    def getLoginResponseDom(self, username, password):
        loginRequest = soapMessage(self.loginRequest%(username, password))
        return parseString(getServerReply(loginRequest))

    logoutRequest = """<bfg:logout>
                         <bfg:request>
                            <header>
                               <clientStamp>0</clientStamp>
                               <sessionToken>%s</sessionToken>
                            </header>
                         </bfg:request>
                      </bfg:logout>"""

    def getLogoutResponseDom(self, sessionToken):
        logoutRequest = soapMessage(self.logoutRequest%(sessionToken))
        return parseString(getServerReply(logoutRequest))
    
    getAllEventTypesRequest = """<bfg:getAllEventTypes>
         <bfg:request>
            <header>
               <clientStamp>0</clientStamp>
               <sessionToken>%s</sessionToken>
            </header>
            <locale>en_UK</locale>
         </bfg:request>
      </bfg:getAllEventTypes>"""

    def test_that_fixed_dummy_list_of_event_types_is_returned(self):
        request = soapMessage(self.getAllEventTypesRequest)
        responseDom = parseString(getServerReply(request))
        self.assertEqual(textFromElement(responseDom, "name", 0), "Football")
        self.assertEqual(textFromElement(responseDom, "id", 0), "121005")
        self.assertErrorCodeInHeaderIs(responseDom, betfair_api.ERROR_CODE_OK)
    
    getEventsRequest = """<bfg:getEvents>
         <bfg:request>
            <header>
               <clientStamp>0</clientStamp>
               <sessionToken>%s</sessionToken>
            </header>
            <eventParentId>%s</eventParentId>
            <locale>en_UK</locale>
         </bfg:request>
      </bfg:getEvents>"""
      
    def test_that_list_of_football_parent_events_is_in_reponse_on_events_by_football_parentid(self):
        loginResponseDom = self.getLoginResponseDom(adapter_context.TEST_SMK_PASSWORD, adapter_context.TEST_SMK_LOGIN)
        validSessionToken = self.sessionTokenFrom(loginResponseDom)
        footballEventTypeId = "121005"
        request = soapMessage(self.getEventsRequest%(validSessionToken, footballEventTypeId))
        responseXml = getServerReply(request)
        responseDom = parseString(responseXml)

        self.getLogoutResponseDom(validSessionToken)
        
        self.assertEqual(textFromElement(responseDom, "eventTypeId", 0), footballEventTypeId)
        self.assertEqual(textFromElement(responseDom, "eventParentId", 0), footballEventTypeId)

        self.assertErrorCodeInHeaderIs(responseDom, betfair_api.ERROR_CODE_OK)
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_CODE_OK)

def getServerReply(request):
    http_conn = httplib.HTTP(HOST, PORT)
    http_conn.putrequest('POST', BETFAIR_SERVICE)
    http_conn.putheader('Host', HOST)
    http_conn.putheader('Content-Type', 'text/xml; charset="utf-8"')
    http_conn.putheader('Content-Length', str(len(request)))
    http_conn.putheader('SOAPAction', '')
    http_conn.endheaders()
    http_conn.send(request)
    (status_code, message, reply_headers) = http_conn.getreply() 
    response = http_conn.getfile().read() 
    return response


def textFromElement(dom, elementName, elementPosition):
    return dom.getElementsByTagName(elementName)[elementPosition].firstChild.nodeValue

SOAP_ENVELOPE = """<?xml version="1.0" encoding="UTF-8"?>
                    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:bfg="http://www.betfair.com/publicapi/v3/BFGlobalService/">
                       <soapenv:Header/>
                       <soapenv:Body>%s</soapenv:Body>
                    </soapenv:Envelope>
                """

def soapMessage(body):
    return SOAP_ENVELOPE%(body)