from xmlrpclib import datetime

from smarkets.exceptions import SocketDisconnected

from betfair.BFGlobalService_types import bfg

from business_layer import BusinessUnit
import smk_api

ERROR_CODE_OK = "OK"
ERROR_INVALID_USERNAME_OR_PASSWORD = "INVALID_USERNAME_OR_PASSWORD"
ERROR_NO_SESSION = "NO_SESSION"
ERROR_API_ERROR = "API_ERROR"

DEFAULT_CURRENCY = "GBP"

BUSINESS_UNIT = BusinessUnit()

def currentDateTime():
    return list(datetime.datetime.now().timetuple())

def createHeader(response, errorCode, sessionToken, soapBinding, typeDefinition):
    response._header = bfg.APIResponseHeader_Def(soapBinding, typeDefinition)
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
    loginResp = bfg.LoginResp_Def(soapBinding, typeDefinition)
    
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
    logoutResp = bfg.LogoutResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, logoutResp, soapBinding, typeDefinition)
    
    logoutActionResult = BUSINESS_UNIT.logUserOutAndReturnResultOfAction(sessionToken)
    
    if logoutActionResult :
        logoutResp._errorCode = ERROR_CODE_OK
    else:
        logoutResp._errorCode = ERROR_API_ERROR

    logoutResponse._Result = logoutResp
    return logoutResponse

def getAllEventTypes(soapBinding, typeDefinition, request, response):
    resp = bfg.GetEventTypesResp_Def(soapBinding, typeDefinition)
    
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    resp._errorCode = ERROR_CODE_OK
    
    if sessionToken:
        resp._eventTypeItems = bfg.ArrayOfEventType_Def(soapBinding, typeDefinition)
        footballEventType  = bfg.EventType_Def(soapBinding, typeDefinition)
        footballEventType._id = smk_api.FOOTBALL_EVENT_TYPE_ID
        footballEventType._name = "Football"
        footballEventType._nextMarketId = 0
        footballEventType._exchangeId = 0
        resp._eventTypeItems._EventType = [footballEventType]

    response._Result = resp
    return response

def event(eventDTO, soapBinding, typeDefinition):
    event = bfg.BFEvent_Def(soapBinding, typeDefinition)
    event._eventId = eventDTO.eventId
    event._eventName = eventDTO.eventName
    event._eventTypeId = eventDTO.eventTypeId
    event._menuLevel = 0#don't know what to use
    event._orderIndex = 0#don't know what to use
    event._startTime = currentDateTime()#use constant 0001-01-01T00:00:00.000Z instead
    event._timezone = "Greenwich Mean Time"#constant
    return event

def market(marketDTO, soapBinding, typeDefinition):
    market = bfg.MarketSummary_Def(soapBinding, typeDefinition)
    market._eventTypeId = marketDTO.marketTypeId
    market._marketId = marketDTO.marketId
    market._marketName = marketDTO.marketName
    market._marketType = "A"#<marketType xsi:type="n2:MarketTypeEnum">A</marketType>
    market._marketTypeVariant = "ADL"#<marketTypeVariant xsi:type="n2:MarketTypeVariantEnum">ADL</marketTypeVariant>
    market._menuLevel = 6 # <menuLevel xsi:type="xsd:int">6</menuLevel>
    market._orderIndex = 2638500 # <orderIndex xsi:type="xsd:int">2638500</orderIndex>
    market._startTime = currentDateTime()#use constant 0001-01-01T00:00:00.000Z instead # <startTime xsi:type="xsd:dateTime">0001-01-01T00:00:00.000Z</startTime>
    market._timezone = "GMT" # <timezone xsi:type="xsd:string">GMT</timezone>
    market._betDelay = 0 # <betDelay xsi:type="xsd:int">0</betDelay>
    market._numberOfWinners = 0 # <numberOfWinners xsi:type="xsd:int">0</numberOfWinners>
    market._eventParentId = marketDTO.marketParentEventId # <eventParentId xsi:type="xsd:int">26962212</eventParentId>
    market._exchangeId = 1 # <exchangeId xsi:type="xsd:int">1</exchangeId>
    return market


def getEvents(soapBinding, typeDefinition, request, response):
    resp = bfg.GetEventsResp_Def(soapBinding, typeDefinition)

    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    resp._errorCode = ERROR_CODE_OK
    eventParentId = request._request._eventParentId
    resp._eventParentId = eventParentId
    if sessionToken:
        resp._eventItems = bfg.ArrayOfBFEvent_Def(soapBinding, typeDefinition)
        resp._eventItems._BFEvent = []
        resp._marketItems = bfg.ArrayOfMarketSummary_Def(soapBinding, typeDefinition)
        resp._marketItems._MarketSummary = []
        
        events = BUSINESS_UNIT.getTodaysFootballEvents(sessionToken)

        if str(eventParentId) == str(smk_api.FOOTBALL_EVENT_TYPE_ID):
            resp._eventItems._BFEvent = map(lambda eventDTO: event(eventDTO, soapBinding, typeDefinition), events.parents)
        elif str(eventParentId) in events.parentToEvent:
            resp._eventItems._BFEvent = map(lambda eventDTO: event(eventDTO, soapBinding, typeDefinition), events.parentToEvent[str(eventParentId)])
        elif str(eventParentId) in events.eventToMarket :
            resp._marketItems._MarketSummary = map(lambda marketDTO: market(marketDTO, soapBinding, typeDefinition), events.eventToMarket[str(eventParentId)])
        else:
#            must raise an exception - invalid parent id
            resp._errorCode = ERROR_API_ERROR
    else :
        resp._errorCode = ERROR_API_ERROR
    response._Result = resp
    return response
