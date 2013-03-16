from xmlrpclib import datetime

from smarkets.exceptions import SocketDisconnected

from betfair.BFGlobalService_types import bfg
from betfair.BFExchangeService_types import bfe

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
    event._startTime = eventDTO.startTime
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
    market._startTime = marketDTO.startTime
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

        if str(eventParentId) in events.parentToEvent:
            resp._eventItems._BFEvent = map(lambda eventDTO: event(eventDTO, soapBinding, typeDefinition), events.parentToEvent[str(eventParentId)])
            #resp._marketItems._MarketSummary for betfair:markets==smk:contracts
        elif str(eventParentId) in events.marketToContract:
            resp._marketItems._MarketSummary = map(lambda marketDTO: market(marketDTO, soapBinding, typeDefinition), events.marketToContract[str(eventParentId)])
        else:
#            must raise an exception - invalid parent id
            resp._errorCode = ERROR_API_ERROR
    else :
        resp._errorCode = ERROR_API_ERROR
    response._Result = resp
    return response

def getAccountFunds(soapBinding, typeDefinition, request, response):
    resp = bfe.GetAccountFundsResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)
    
    if sessionToken:
        accountStatus = BUSINESS_UNIT.getAccountFunds(sessionToken)
        resp._availBalance = accountStatus.cash#????
        resp._balance = accountStatus.cash#???
        resp._withdrawBalance = accountStatus.cash#???
        resp._exposure = accountStatus.exposure#???
        
        
        resp._commissionRetain = 0.0000#???
        resp._creditLimit = 0.0000#???
        resp._currentBetfairPoints = 0#???
        resp._expoLimit = 0.0000#???
        resp._holidaysAvailable = 0#???
        resp._minorErrorCode = None
        resp._nextDiscount = 0.0000#???
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def placeBets(soapBinding, typeDefinition, request, response):
    resp = bfe.PlaceBetsResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)
    
    if sessionToken:
        resp._betResults = bfe.ArrayOfPlaceBetsResult_Def(soapBinding, typeDefinition)
        resp._betResults._PlaceBetsResult = []
        
        for betRequest in request._request._bets._PlaceBets:
            placeBetResult = bfe.PlaceBetsResult_Def(soapBinding, typeDefinition)
            sizeInPounds = betRequest._size
            priceInProcentsMultipliedBy100 = betRequest._price
            marketId = betRequest._marketId
            contractId = betRequest._selectionId
            betResult = BUSINESS_UNIT.placeBet(sessionToken, marketId, contractId, sizeInPounds, int(priceInProcentsMultipliedBy100))
            
            placeBetResult._averagePriceMatched = sizeInPounds#???
            placeBetResult._sizeMatched = sizeInPounds#???
            placeBetResult._betId = betResult.id
            placeBetResult._resultCode = "OK"
            placeBetResult._success = True
            resp._betResults._PlaceBetsResult.append(placeBetResult)
    
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def cancelBets(soapBinding, typeDefinition, request, response):
    resp = bfe.CancelBetsResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)
    
    if sessionToken:
        resp._betResults = bfe.ArrayOfCancelBetsResult_Def(soapBinding, typeDefinition)
        resp._betResults._CancelBetsResult = []
        
        for cancelBetRequest in request._request._bets._CancelBets:
            cancelBetResult = bfe.CancelBetsResult_Def(soapBinding, typeDefinition)
            betId = cancelBetRequest._betId
            originalCancelBetResult = BUSINESS_UNIT.cancelBet(sessionToken, betId)
            cancelBetResult._betId = betId
            cancelBetResult._resultCode = "OK"
            cancelBetResult._sizeCancelled = 000.0000#???
            cancelBetResult._sizeMatched = 000.0000#???
            cancelBetResult._success = True
            resp._betResults._CancelBetsResult.append(cancelBetResult)
        
    
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def getCurrentBets(soapBinding, typeDefinition, request, response):
    resp = bfe.GetCurrentBetsResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)
    
    if sessionToken:
        resp._bets = bfe.ArrayOfBet_Def(soapBinding, typeDefinition)
        resp._bets._Bet = []
        betsForAccount = BUSINESS_UNIT.getBetsForAccount(sessionToken)
        for betDetails in betsForAccount.bets:
            bet = bfe.Bet_Def(soapBinding, typeDefinition)
            bet._asianLineId=0#change
            bet._avgPrice=betDetails.price#?
            bet._betId=betDetails.id
            bet._betStatus = "U"#change
            bet._betType = "B"#or L, change
            bet._betCategoryType="NONE"
            bet._betPersistenceType="NONE"
            
            bet._cancelledDate = currentDateTime()
            bet._lapsedDate = currentDateTime()
            bet._marketId = betDetails.marketId
            # bet._marketName = "someName"#optional
            # bet._fullMarketName = "someName"#change
            bet._marketType = "NOT_APPLICABLE"
            bet._marketTypeVariant = "D"#Default
            bet._matchedDate = currentDateTime()
            bet._matchedSize = betDetails.quantity#?
            bet._matches = None
            bet._placedDate = currentDateTime()
            bet._price = betDetails.price
            bet._bspLiability = betDetails.quantity#?
            bet._profitAndLoss = 00000.00#nillable
            bet._selectionId = betDetails.contractId
            bet._selectionName = None
            bet._settledDate = currentDateTime()
            bet._remainingSize = betDetails.quantity#?
            bet._requestedSize = betDetails.quantity#?
            bet._voidedDate = currentDateTime()
            bet._handicap = 0.00#change
            
            resp._bets._Bet.append(bet)
        
    
    resp._errorCode = ERROR_CODE_OK
    resp._totalRecordCount = 0
    response._Result = resp
    return response