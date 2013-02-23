from xmlrpclib import datetime

from smarkets.exceptions import SocketDisconnected

from betfair.BFGlobalService_types import *
from business_layer import BusinessUnit
import business_layer

ERROR_CODE_OK = "OK"
ERROR_INVALID_USERNAME_OR_PASSWORD = "INVALID_USERNAME_OR_PASSWORD"
ERROR_NO_SESSION = "NO_SESSION"
ERROR_API_ERROR = "API_ERROR"

DEFAULT_CURRENCY = "GBP"

BUSINESS_UNIT = BusinessUnit()

def currentDateTime():
    return list(datetime.datetime.now().timetuple())

def createHeader(response, errorCode, sessionToken, soapBinding, typeDefinition):
    response._header = ns0.APIResponseHeader_Def(soapBinding, typeDefinition)
    response._header._timestamp = currentDateTime()
    response._header._sessionToken = sessionToken
    response._header._errorCode = errorCode

def addHeaderToResponseAndValidateSession(request, response, soapBinding, typeDefinition):
    sessionToken = request._request._header._sessionToken
    client = BUSINESS_UNIT.getClientIfTokenIsValid(sessionToken)
    if client :
        createHeader(response, ERROR_CODE_OK, sessionToken, soapBinding, typeDefinition)
        return sessionToken
    else :
        createHeader(response, ERROR_NO_SESSION, None, soapBinding, typeDefinition)
        return None


#+covered with acceptance test as verbose to unit test of markup generation
def login(soapBinding, typeDefinition, request, loginResponse):
    loginResp = ns0.LoginResp_Def(soapBinding, typeDefinition)
    
    username = request._request._username
    password = request._request._password

    try:
        sessionToken = BUSINESS_UNIT.authenticateUserAndReturnHisSessionToken(username, password)
        createHeader(loginResp, ERROR_CODE_OK, sessionToken, soapBinding, typeDefinition)
        loginResp._errorCode = ERROR_CODE_OK
    except SocketDisconnected:
        createHeader(loginResp, ERROR_CODE_OK, None, soapBinding, typeDefinition)
        loginResp._errorCode = ERROR_INVALID_USERNAME_OR_PASSWORD

    loginResp._minorErrorCode = "age.verification.required"
    loginResp._validUntil = currentDateTime()
    loginResp._currency = DEFAULT_CURRENCY

    loginResponse._Result = loginResp
    return loginResponse


def logout(soapBinding, typeDefinition, request, logoutResponse):
    logoutResp = ns0.LogoutResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, logoutResp, soapBinding, typeDefinition)
    
    logoutActionResult = BUSINESS_UNIT.logUserOutAndReturnResultOfAction(sessionToken)
    
    if logoutActionResult :
        logoutResp._errorCode = ERROR_CODE_OK
    else:
        logoutResp._errorCode = ERROR_API_ERROR

    logoutResponse._Result = logoutResp
    return logoutResponse

def getAllEventTypes(soapBinding, typeDefinition, request, response):
    resp = ns0.GetEventTypesResp_Def(soapBinding, typeDefinition)
    
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    resp._errorCode = ERROR_CODE_OK
    
    if sessionToken:
        resp._eventTypeItems = ns0.ArrayOfEventType_Def(soapBinding, typeDefinition)
        footballEventType  = ns0.EventType_Def(soapBinding, typeDefinition)
        footballEventType._id = business_layer.FOOTBALL_EVENT_TYPE_ID
        footballEventType._name = "Football"
        footballEventType._nextMarketId = 0
        footballEventType._exchangeId = 0
        resp._eventTypeItems._EventType = [footballEventType]

    response._Result = resp
    return response

def event(eventId, eventName, eventTypeId, soapBinding, typeDefinition):
    event = ns0.BFEvent_Def(soapBinding, typeDefinition)
    event._eventId = eventId
    event._eventName = eventName
    event._eventTypeId = eventTypeId
    event._menuLevel = 0#don't know what to use
    event._orderIndex = 0#don't know what to use
    event._startTime = currentDateTime()#use constant 0001-01-01T00:00:00.000Z instead
    event._timezone = "Greenwich Mean Time"#constant
    return event

class Events(object):
    def __init__(self):
        self.parents = []
        self.parentChildren={}

def getEvents(soapBinding, typeDefinition, request, response):
    resp = ns0.GetEventsResp_Def(soapBinding, typeDefinition)

    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    resp._errorCode = ERROR_CODE_OK
    eventParentId = request._request._eventParentId
    resp._eventParentId = eventParentId
    if sessionToken:
        resp._eventItems = ns0.ArrayOfBFEvent_Def(soapBinding, typeDefinition)
        resp._eventItems._BFEvent = []
        
        eventsMessage = BUSINESS_UNIT.getTodaysFootballEvents(sessionToken)
        events = Events()
        for parent in eventsMessage.parents:
            events.parents.append(event(parent.event.low, parent.name, request._request._eventParentId, soapBinding, typeDefinition))
            events.parentChildren[str(parent.event.low)]=[]
        for sportEvent in eventsMessage.with_markets:
            events.parentChildren[str(sportEvent.parent.low)].append(event(sportEvent.event.low, sportEvent.name, business_layer.FOOTBALL_EVENT_TYPE_ID, soapBinding, typeDefinition))
        
        if str(eventParentId) == str(business_layer.FOOTBALL_EVENT_TYPE_ID):
            resp._eventItems._BFEvent = events.parents
        elif str(eventParentId) in events.parentChildren:
            resp._eventItems._BFEvent = events.parentChildren[str(eventParentId)]
        else :
            print "do nothing for now, must display events or markets"
    else :
        resp._errorCode = ERROR_API_ERROR
    response._Result = resp
    return response
