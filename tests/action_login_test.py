import unittest

from BFGlobalService_types import *
import action_login
import BFGlobalService_server

class LoginActionTest(unittest.TestCase):
    webService = BFGlobalService_server.BFGlobalService()

    #DUMMY, we shouldn't give input as XML in unit tests
    def test_that_login_should_return_dummy_valid_ok_response(self):
        #given
        request = """<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:bfg="http://www.betfair.com/publicapi/v3/BFGlobalService/">
           <soapenv:Header/>
           <soapenv:Body>
              <bfg:login>
                 <bfg:request>
                    <ipAddress>0</ipAddress>
                    <locationId>0</locationId>
                    <password>*********</password>
                    <productId>82</productId>
                    <username>mylogin</username>
                    <vendorSoftwareId>0</vendorSoftwareId>
                 </bfg:request>
              </bfg:login>
           </soapenv:Body>
        </soapenv:Envelope>"""
        parsedSoap = ZSI.parse.ParsedSoap(request, None)
        #when
        loginResponse = action_login.login(self.webService, parsedSoap, parsedSoap.dom, ns1.loginResponse_Dec())
        #then
        self.assertEqual(loginResponse._Result._errorCode, action_login.ERROR_CODE_OK)
