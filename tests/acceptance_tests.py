import unittest

import httplib
from xml.dom.minidom import parseString

import session_management_actions
import adapter_context
import time

HOST="localhost"
PORT=int(adapter_context.BETFAIR_API_PORT)
BETFAIR_SERVICE = "/BFGlobalService"

ERROR_CODE_TAG="errorCode"
SESSION_TOKEN_TAG="sessionToken"

class SessionManagementAcceptanceTest(unittest.TestCase):

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

    def test_that_valid_credentials_are_causing_successful_login(self):
        responseDom = self.getLoginResponseDom(adapter_context.SMK_PASSWORD, adapter_context.SMK_LOGIN)
        
        self.assertEquals(textFromElement(responseDom, ERROR_CODE_TAG, 1), session_management_actions.ERROR_CODE_OK)
        sessionToken = textFromElement(responseDom, SESSION_TOKEN_TAG, 0)
        self.assertEquals(len(sessionToken), session_management_actions.SESSION_TOKEN_LENGTH)

        self.getLogoutResponseDom(sessionToken)

    def test_that_invalid_credentials_are_causing_login_failure(self):
        responseDom = self.getLoginResponseDom('wrongLogin_' + str(time.time()), 'wrongPassword')
        
        self.assertEquals(textFromElement(responseDom, ERROR_CODE_TAG, 1), session_management_actions.ERROR_INVALID_USERNAME_OR_PASSWORD)
        self.assertEquals(responseDom.getElementsByTagName(SESSION_TOKEN_TAG)[0].firstChild, None)


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


    def test_that_logout_with_nonexisting_session_token_results_unsuccessfuly(self):
        responseDom = self.getLogoutResponseDom("invalidSessionToken")

        self.assertEquals(textFromElement(responseDom, ERROR_CODE_TAG, 0), session_management_actions.ERROR_NO_SESSION)
        self.assertEquals(textFromElement(responseDom, ERROR_CODE_TAG, 1), session_management_actions.ERROR_API_ERROR)

    def test_that_logout_with_valid_session_token_results_successfuly(self):
        responseDom = self.getLoginResponseDom(adapter_context.SMK_PASSWORD, adapter_context.SMK_LOGIN)
        validSessionToken = textFromElement(responseDom, SESSION_TOKEN_TAG, 0)
        responseDom = self.getLogoutResponseDom(validSessionToken)

        self.assertEquals(textFromElement(responseDom, ERROR_CODE_TAG, 0), session_management_actions.ERROR_CODE_OK)
        self.assertEquals(textFromElement(responseDom, ERROR_CODE_TAG, 1), session_management_actions.ERROR_CODE_OK)


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