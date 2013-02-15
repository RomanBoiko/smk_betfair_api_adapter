from BFGlobalService_types import *
from xmlrpclib import datetime
import smk_api
from smarkets.exceptions import SocketDisconnected
import uuid

ERROR_CODE_OK = "OK"
ERROR_INVALID_USERNAME_OR_PASSWORD = "INVALID_USERNAME_OR_PASSWORD"
ERROR_NO_SESSION = "NO_SESSION"
ERROR_API_ERROR = "API_ERROR"

DEFAULT_CURRENCY = "GBP"

SESSION_TOKEN_LENGTH=32

SESSIONS_CACHE={}

#-refactor
#-cover with units
#-add currency and other personal data
#+covered with acceptance test
def login(soapBinding, typeDefinition, request, loginResponse):
    dateTime = currentDateTime()

    loginResp = ns0.LoginResp_Def(soapBinding, typeDefinition)
    loginResp._header = ns0.APIResponseHeader_Def(soapBinding, typeDefinition)
    loginResp._header._errorCode = ERROR_CODE_OK
    loginResp._header._timestamp = dateTime
    loginResp._currency = DEFAULT_CURRENCY
    
    username = request._request._username
    password = request._request._password
    try:
        client = smk_api.login(username, password)
        sessionToken = newSessionId()
        loginResp._header._sessionToken = sessionToken
        loginResp._errorCode = ERROR_CODE_OK
        SESSIONS_CACHE[sessionToken] = client
        smk_api.logout(client)
    except SocketDisconnected:
        loginResp._errorCode = ERROR_INVALID_USERNAME_OR_PASSWORD
    loginResp._validUntil = dateTime
    loginResponse._Result = loginResp
    return loginResponse

def currentDateTime():
    return list(datetime.datetime.now().timetuple())

def newSessionId():
    return uuid.uuid4().hex

def logout(soapBinding, typeDefinition, request, logoutResponse):
    logoutResp = ns0.LogoutResp_Def(soapBinding, typeDefinition)
    logoutResp._header = ns0.APIResponseHeader_Def(soapBinding, typeDefinition)
    logoutResp._header._errorCode = ERROR_NO_SESSION
    logoutResp._header._timestamp = currentDateTime()
    logoutResp._header._sessionToken = None
    logoutResp._errorCode = ERROR_API_ERROR
    logoutResponse._Result = logoutResp
    return logoutResponse

#<?xml version="1.0" encoding="UTF-8"?>
#<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:n2="http://www.betfair.com/publicapi/types/global/v3/" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
#   <soap:Body>
#      <n:logoutResponse xmlns:n="http://www.betfair.com/publicapi/v3/BFGlobalService/">
#         <n:Result xsi:type="n2:LogoutResp">
#            <header xsi:type="n2:APIResponseHeader">
#               <errorCode xsi:type="n2:APIErrorEnum">NO_SESSION</errorCode>
#               <minorErrorCode xsi:nil="1"/>
#               <sessionToken xsi:nil="1"/>
#               <timestamp xsi:type="xsd:dateTime">2013-02-11T17:36:30.061Z</timestamp>
#            </header>
#            <minorErrorCode xsi:nil="1"/>
#            <errorCode xsi:type="n2:LogoutErrorEnum">API_ERROR</errorCode>
#         </n:Result>
#      </n:logoutResponse>
#   </soap:Body>
#</soap:Envelope>
