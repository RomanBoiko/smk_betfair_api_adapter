import unittest

from BFGlobalService_types import *
import action_login
import BFGlobalService_server

#import requests
import httplib
from xml.dom import minidom

class AcceptanceTest(unittest.TestCase):
    webService = BFGlobalService_server.BFGlobalService()

    def test_that_login_should_return_dummy_valid_ok_response(self):
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

        response = self.getServerReply(request)
        print(response)
        self.assertIn("<errorCode>OK</errorCode>", response)

    def getServerReply(self, request):
        port=8080
        host="localhost"
        http_conn = httplib.HTTP(host, port)
        http_conn.putrequest('POST', "/BFGlobalService")
        http_conn.putheader('Host', host)
        http_conn.putheader('Content-Type', 'text/xml; charset="utf-8"')
        http_conn.putheader('Content-Length', str(len(request)))
        http_conn.putheader('SOAPAction', '')
        http_conn.endheaders()
        http_conn.send(request)
        (status_code, message, reply_headers) = http_conn.getreply() 
        response = http_conn.getfile().read() 
        return response

