from betfair.BFGlobalService_types import *
from xmlrpclib import datetime
from smarkets.exceptions import SocketDisconnected
from business_layer import BusinessUnit
from smk_api import EventsBroker, SmkDate
import smk_api
import adapter_context
import smarkets

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

def getAllEventTypes(soapBinding, typeDefinition, request, response):
    resp = ns0.GetEventTypesResp_Def(soapBinding, typeDefinition)
    resp._header = ns0.APIResponseHeader_Def(soapBinding, typeDefinition)
    resp._header._errorCode = ERROR_CODE_OK
    resp._header._timestamp = currentDateTime()
#   todo: to validate token
    resp._header._sessionToken = request._request._header._sessionToken
    resp._errorCode = ERROR_CODE_OK
    
    resp._eventTypeItems = ns0.ArrayOfEventType_Def(soapBinding, typeDefinition)
    footballEventType  = ns0.EventType_Def(soapBinding, typeDefinition)
    footballEventType._id = 121005
    footballEventType._name = "Football"
    footballEventType._nextMarketId = 0
    footballEventType._exchangeId = 0

    resp._eventTypeItems._EventType = [footballEventType] 
    response._Result = resp
    return response

def event(eventId, eventName, eventParentId, soapBinding, typeDefinition):
    event = ns0.BFEvent_Def(soapBinding, typeDefinition)
    event._eventId = eventId
    event._eventName = eventName
    event._eventTypeId = eventParentId
    event._menuLevel = 0#don't know what to use
    event._orderIndex = 0#don't know what to use
    event._startTime = currentDateTime()#use constant 0001-01-01T00:00:00.000Z instead
    event._timezone = "Greenwich Mean Time"#constant
    return event

def getEvents(soapBinding, typeDefinition, request, response):
    resp = ns0.GetEventsResp_Def(soapBinding, typeDefinition)
    resp._header = ns0.APIResponseHeader_Def(soapBinding, typeDefinition)
    resp._header._errorCode = ERROR_CODE_OK
    resp._header._timestamp = currentDateTime()
    #   todo: to validate token
    resp._header._sessionToken = request._request._header._sessionToken
    resp._errorCode = ERROR_CODE_OK
    resp._eventParentId = request._request._eventParentId
    
    resp._eventItems = ns0.ArrayOfBFEvent_Def(soapBinding, typeDefinition)
    resp._eventItems._BFEvent = []
    client = BUSINESS_UNIT.getClientIfTokenIsValid(resp._header._sessionToken)
    if client :
        eventsBroker = EventsBroker()
        eventsMessage = eventsBroker.getEvents(client, smarkets.events.FootballByDate(SmkDate()))
        for parent in eventsMessage.parents:
            resp._eventItems._BFEvent.append(event(parent.event.low, parent.name, request._request._eventParentId, soapBinding, typeDefinition))
    else:
        resp._header._errorCode = ERROR_NO_SESSION
        resp._errorCode = ERROR_API_ERROR
    response._Result = resp
    return response
