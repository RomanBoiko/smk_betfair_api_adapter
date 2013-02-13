import unittest

import httplib
import BFGlobalService_server

from BFGlobalService_types import *
import action_login

HOST="localhost"
PORT=8080
BETFAIR_SERVICE = "/BFGlobalService"

class AcceptanceTest(unittest.TestCase):

    loginRequest = """<?xml version="1.0" encoding="UTF-8"?>
                    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:bfg="http://www.betfair.com/publicapi/v3/BFGlobalService/">
                       <soapenv:Header/>
                       <soapenv:Body>
                          <bfg:login>
                             <bfg:request>
                                <ipAddress>0</ipAddress>
                                <locationId>0</locationId>
                                <password>%s</password>
                                <productId>82</productId>
                                <username>%s</username>
                                <vendorSoftwareId>0</vendorSoftwareId>
                             </bfg:request>
                          </bfg:login>
                       </soapenv:Body>
                    </soapenv:Envelope>"""

    def test_that_valid_credentials_are_causing_successful_login(self):
        response = self.getServerReply(self.loginRequest%("password", "login"))
        parserResponse = ZSI.parse.ParsedSoap(response, None).Parse(BFGlobalService_server.loginOut.typecode)

        self.assertEquals(parserResponse._Result._errorCode, action_login.ERROR_CODE_OK)
        self.assertGreater(len(parserResponse._Result._header._sessionToken), 0)

    def test_that_invalid_credentials_are_causing_login_failure(self):
        response = self.getServerReply(self.loginRequest%("wrongpassword", "wronglogin"))
        parserResponse = ZSI.parse.ParsedSoap(response, None).Parse(BFGlobalService_server.loginOut.typecode)

        self.assertEquals(parserResponse._Result._errorCode, action_login.ERROR_INVALID_USERNAME_OR_PASSWORD)
        self.assertEquals(parserResponse._Result._header._sessionToken, None)




    def getServerReply(self, request):
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

