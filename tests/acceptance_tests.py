import httplib
import time
import unittest
from xml.dom.minidom import parseString

import adapter_context
import betfair_api
import business_layer

HOST="localhost"
PORT=int(adapter_context.BETFAIR_API_PORT)
BETFAIR_SERVICE = "/BFGlobalService"

ERROR_CODE_TAG="errorCode"
SESSION_TOKEN_TAG="sessionToken"

SOAP_ENVELOPE = """<?xml version="1.0" encoding="UTF-8"?>
                    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:bfg="http://www.betfair.com/publicapi/v3/BFGlobalService/">
                       <soapenv:Header/>
                       <soapenv:Body>%s</soapenv:Body>
                    </soapenv:Envelope>
                """

loginRequestTemplate = """<bfg:login>
                             <bfg:request>
                                <ipAddress>0</ipAddress>
                                <locationId>0</locationId>
                                <password>%s</password>
                                <productId>82</productId>
                                <username>%s</username>
                                <vendorSoftwareId>0</vendorSoftwareId>
                             </bfg:request>
                          </bfg:login>"""

logoutRequestTemplate = """<bfg:logout>
                             <bfg:request>
                                <header>
                                   <clientStamp>0</clientStamp>
                                   <sessionToken>%s</sessionToken>
                                </header>
                             </bfg:request>
                          </bfg:logout>"""

getEventsRequestTemplate = """<bfg:getEvents>
                                 <bfg:request>
                                    <header>
                                       <clientStamp>0</clientStamp>
                                       <sessionToken>%s</sessionToken>
                                    </header>
                                    <eventParentId>%s</eventParentId>
                                    <locale>en_UK</locale>
                                 </bfg:request>
                              </bfg:getEvents>"""

getAllEventTypesRequestTemplate = """<bfg:getAllEventTypes>
                                 <bfg:request>
                                    <header>
                                       <clientStamp>0</clientStamp>
                                       <sessionToken>%s</sessionToken>
                                    </header>
                                    <locale>en_UK</locale>
                                 </bfg:request>
                              </bfg:getAllEventTypes>"""

class AdapterAcceptanceTest(unittest.TestCase):
    def assertErrorCodeInHeaderIs(self, response, expectedErrorCode):
        self.assertEquals(textFromElement(response, ERROR_CODE_TAG, 0), expectedErrorCode)
    def assertResultErrorCodeIs(self, response, expectedErrorCode):
        self.assertEquals(textFromElement(response, ERROR_CODE_TAG, 1), expectedErrorCode)
    def assertErrorCodesAreOk(self, responseDom):
        self.assertErrorCodeInHeaderIs(responseDom, betfair_api.ERROR_CODE_OK)
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_CODE_OK)

class SessionManagementAcceptanceTest(AdapterAcceptanceTest):

    def test_that_valid_credentials_are_causing_successful_login(self):
        responseDom = getLoginResponseDom(adapter_context.TEST_SMK_PASSWORD, adapter_context.TEST_SMK_LOGIN)
        
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_CODE_OK)
        sessionToken = sessionTokenFrom(responseDom)
        self.assertGreater(len(sessionToken), 0)

        getLogoutResponseDom(sessionToken)

    def test_that_invalid_credentials_are_causing_login_failure(self):
        responseDom = getLoginResponseDom('wrongLogin_' + str(time.time()), 'wrongPassword')
        
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_INVALID_USERNAME_OR_PASSWORD)
        self.assertEquals(responseDom.getElementsByTagName(SESSION_TOKEN_TAG)[0].firstChild, None)

    def test_that_logout_with_nonexisting_session_token_results_unsuccessfuly(self):
        responseDom = getLogoutResponseDom("invalidSessionToken")
        #THEN
        self.assertErrorCodeInHeaderIs(responseDom, betfair_api.ERROR_NO_SESSION)
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_API_ERROR)

    def test_that_logout_with_valid_session_token_results_successfuly(self):
        loginResponseDom = getLoginResponseDom(adapter_context.TEST_SMK_PASSWORD, adapter_context.TEST_SMK_LOGIN)
        validSessionToken = sessionTokenFrom(loginResponseDom)
        logoutResponseDom = getLogoutResponseDom(validSessionToken)
        #THEN
        self.assertErrorCodesAreOk(logoutResponseDom)


class EventsRetrievingTest(AdapterAcceptanceTest):

    @classmethod
    def setUpClass(cls):
        loginResponseDom = getLoginResponseDom(adapter_context.TEST_SMK_PASSWORD, adapter_context.TEST_SMK_LOGIN)
        EventsRetrievingTest.validSessionToken = sessionTokenFrom(loginResponseDom)

    @classmethod
    def tearDownClass(cls):
        getLogoutResponseDom(EventsRetrievingTest.validSessionToken)

    def test_that_fixed_dummy_list_of_event_types_is_returned(self):
        request = soapMessage(getAllEventTypesRequestTemplate%EventsRetrievingTest.validSessionToken)
        responseDom = parseString(getServerReply(request))
        self.assertEqual(textFromElement(responseDom, "name", 0), "Football")
        self.assertEqual(textFromElement(responseDom, "id", 0), str(business_layer.FOOTBALL_EVENT_TYPE_ID))
        self.assertErrorCodesAreOk(responseDom)
    
      
    def test_that_list_of_football_parent_events_is_in_reponse_on_events_by_football_parentid(self):
        footballEventTypeId = str(business_layer.FOOTBALL_EVENT_TYPE_ID)
        request = soapMessage(getEventsRequestTemplate%(EventsRetrievingTest.validSessionToken, footballEventTypeId))
        responseDom = parseString(getServerReply(request))

        self.assertEqual(textFromElement(responseDom, "eventTypeId", 0), footballEventTypeId)
        self.assertEqual(textFromElement(responseDom, "eventParentId", 0), footballEventTypeId)

        self.assertErrorCodesAreOk(responseDom)

        parentEventId = textFromElement(responseDom, "eventId", 0)
        self.check_that_event_children_can_be_retreived_by_getEvents_request(parentEventId, footballEventTypeId)

    def check_that_event_children_can_be_retreived_by_getEvents_request(self, parentEventId, eventTypeId):
        request = soapMessage(getEventsRequestTemplate%(EventsRetrievingTest.validSessionToken, parentEventId))
        responseXml = getServerReply(request)
        responseDom = parseString(responseXml)
        self.assertEqual(textFromElement(responseDom, "eventParentId", 0), parentEventId)
        self.assertEqual(textFromElement(responseDom, "eventTypeId", 0), eventTypeId)

###############################################
# Common utils to operate with Betfair SOAP API
###############################################
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

def getLogoutResponseDom(sessionToken):
    logoutRequest = soapMessage(logoutRequestTemplate%(sessionToken))
    return parseString(getServerReply(logoutRequest))

def getLoginResponseDom(username, password):
    loginRequest = soapMessage(loginRequestTemplate%(username, password))
    response = getServerReply(loginRequest)
    return parseString(response)

def textFromElement(dom, elementName, elementPosition):
    return dom.getElementsByTagName(elementName)[elementPosition].firstChild.nodeValue

def sessionTokenFrom(response):
    return textFromElement(response, SESSION_TOKEN_TAG, 0)

def soapMessage(body):
    return SOAP_ENVELOPE%(body)
