from BFGlobalService_types import *
from xmlrpclib import datetime

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
    if request._request._username == "username":
        loginResp._header._sessionToken = "dummySessionToken"
        loginResp._errorCode = ERROR_CODE_OK
    else:
        loginResp._errorCode = ERROR_INVALID_USERNAME_OR_PASSWORD
    loginResp._validUntil = dateTime
    loginResponse._Result = loginResp
    return loginResponse

def currentDateTime():
    return list(datetime.datetime.now().timetuple())