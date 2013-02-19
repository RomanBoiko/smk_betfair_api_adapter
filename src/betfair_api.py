from betfair.BFGlobalService_types import *
from xmlrpclib import datetime
from smarkets.exceptions import SocketDisconnected
from business_layer import BusinessUnit

ERROR_CODE_OK = "OK"
ERROR_INVALID_USERNAME_OR_PASSWORD = "INVALID_USERNAME_OR_PASSWORD"
ERROR_NO_SESSION = "NO_SESSION"
ERROR_API_ERROR = "API_ERROR"

DEFAULT_CURRENCY = "GBP"

BUSINESS_UNIT = BusinessUnit()

def currentDateTime():
    return list(datetime.datetime.now().timetuple())

#+covered with acceptance test as verbose to unit test of markup generation
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
        sessionToken = BUSINESS_UNIT.authenticateUserAndReturnHisSessionToken(username, password)
        loginResp._header._sessionToken = sessionToken
        loginResp._errorCode = ERROR_CODE_OK
    except SocketDisconnected:
        loginResp._errorCode = ERROR_INVALID_USERNAME_OR_PASSWORD

    loginResp._minorErrorCode = "age.verification.required"
    loginResp._validUntil = dateTime
    loginResponse._Result = loginResp
    return loginResponse


def logout(soapBinding, typeDefinition, request, logoutResponse):
    logoutResp = ns0.LogoutResp_Def(soapBinding, typeDefinition)
    logoutResp._header = ns0.APIResponseHeader_Def(soapBinding, typeDefinition)
    logoutResp._header._timestamp = currentDateTime()
    logoutResp._header._sessionToken = None
    
    sessionToken = request._request._header._sessionToken
    logoutActionResult = BUSINESS_UNIT.logUserOutAndReturnResultOfAction(sessionToken)
    
    if logoutActionResult :
        logoutResp._header._errorCode = ERROR_CODE_OK
        logoutResp._errorCode = ERROR_CODE_OK
    else:
        logoutResp._header._errorCode = ERROR_NO_SESSION
        logoutResp._errorCode = ERROR_API_ERROR

    logoutResponse._Result = logoutResp
    return logoutResponse
