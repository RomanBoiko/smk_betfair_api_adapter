from BFGlobalService_types import *
from xmlrpclib import datetime

ERROR_CODE_OK = "OK"
DEFAULT_CURRENCY = "GBP"



def login(soapBinding, typeDefinition, request, loginResponse):
    dateTime = currentDateTime()

    loginResp = ns0.LoginResp_Def(soapBinding, typeDefinition)
    loginResp._header = ns0.APIResponseHeader_Def(soapBinding, typeDefinition)
    loginResp._header._errorCode = ERROR_CODE_OK
    loginResp._header._timestamp = dateTime
    loginResp._currency = DEFAULT_CURRENCY
    loginResp._errorCode = ERROR_CODE_OK
    loginResp._validUntil = dateTime
    loginResponse._Result = loginResp
    return loginResponse

def currentDateTime():
    return list(datetime.datetime.now().timetuple())