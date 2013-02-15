from BFGlobalService_types import *
from xmlrpclib import datetime
from pprint import pprint
import smk_api
from smarkets.exceptions import SocketDisconnected

ERROR_CODE_OK = "OK"
ERROR_INVALID_USERNAME_OR_PASSWORD = "INVALID_USERNAME_OR_PASSWORD"
DEFAULT_CURRENCY = "GBP"



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
        loginResp._header._sessionToken = "dummySessionToken"
        loginResp._errorCode = ERROR_CODE_OK
        smk_api.logout(client)
    except SocketDisconnected:
        loginResp._errorCode = ERROR_INVALID_USERNAME_OR_PASSWORD
    loginResp._validUntil = dateTime
    loginResponse._Result = loginResp
    return loginResponse

def currentDateTime():
    return list(datetime.datetime.now().timetuple())