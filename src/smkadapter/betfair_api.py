from xmlrpclib import datetime

from betfair.BFGlobalService_types import bfg
from betfair.BFExchangeService_types import bfe

from business_layer import BusinessUnit
import smk_api

ERROR_CODE_OK = "OK"
ERROR_INVALID_USERNAME_OR_PASSWORD = "INVALID_USERNAME_OR_PASSWORD"
ERROR_NO_SESSION = "NO_SESSION"
ERROR_API_ERROR = "API_ERROR"
ERROR_CANNOT_ACCEPT_BET = "CANNOT_ACCEPT_BET"
ERROR_BET_NOT_CANCELLED = "BET_NOT_CANCELLED"

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

def login(soapBinding, typeDefinition, request, loginResponse):
    loginResp = bfg.LoginResp_Def(soapBinding, typeDefinition)
    
    username = request._request._username
    password = request._request._password

    loginResult = BUSINESS_UNIT.authenticateUserAndReturnHisSessionToken(username, password)
    if loginResult.succeeded :
        sessionToken = loginResult.result
        createHeader(loginResp, ERROR_CODE_OK, sessionToken, soapBinding, typeDefinition)
        loginResp._errorCode = ERROR_CODE_OK
        accountStatus = BUSINESS_UNIT.getAccountFunds(sessionToken)
        loginResp._currency = accountStatus.currency
    else:
        createHeader(loginResp, ERROR_CODE_OK, None, soapBinding, typeDefinition)
        loginResp._errorCode = ERROR_INVALID_USERNAME_OR_PASSWORD

    loginResp._minorErrorCode = "age.verification.required"
    loginResp._validUntil = currentDateTime()

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
            isBetTypeBuy = (betRequest._betType == "B")
            
            placeBetResult._averagePriceMatched = sizeInPounds#???
            placeBetResult._sizeMatched = sizeInPounds#???
            betResult = BUSINESS_UNIT.placeBet(sessionToken, marketId, contractId, sizeInPounds, int(priceInProcentsMultipliedBy100), isBetTypeBuy)
            if betResult.succeeded:
                placeBetResult._resultCode = ERROR_CODE_OK
                placeBetResult._success = True
                placeBetResult._betId = betResult.result.id
            else:
                placeBetResult._resultCode = ERROR_CANNOT_ACCEPT_BET
                placeBetResult._success = False
                placeBetResult._betId = 0
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
            if originalCancelBetResult.succeeded:
                cancelBetResult._resultCode = ERROR_CODE_OK
                cancelBetResult._success = True
            else:
                cancelBetResult._resultCode = ERROR_BET_NOT_CANCELLED
                cancelBetResult._success = False
            cancelBetResult._betId = betId
            cancelBetResult._sizeCancelled = 000.0000#???
            cancelBetResult._sizeMatched = 000.0000#???
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
            if betDetails.isBetTypeBuy:
                bet._betType = "B"#BUYER
            else:
                bet._betType = "L"#SELLER
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
        
    
    resp._totalRecordCount = 0
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

######################
#DUMMY IMPLEMENTATIONS
######################
def cancelBetsByMarket(soapBinding, typeDefinition, request, response):
    resp = bfe.CancelBetsByMarketResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        resp._results = bfe.ArrayOfCancelBetsByMarketResult_Def(soapBinding, typeDefinition)
        resp._results._CancelBetsByMarketResult = []
        
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def getMarket(soapBinding, typeDefinition, request, response):
    resp = bfe.GetMarketResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        marketId = request._request._marketId
        resp._market = bfe.Market_Def(soapBinding, typeDefinition)
        resp._market._countryISO3 = "xsd:string" #optional
        resp._market._discountAllowed  = False #?
        resp._market._eventTypeId = 1 #mandatory
        resp._market._lastRefresh = 2 #LONG mandatory
        resp._market._marketBaseRate = 1.0 #FLOAT mandatory
        resp._market._marketDescription = "xsd:string" #optional
        resp._market._marketDescriptionHasDate  = False #mandatory
        resp._market._marketDisplayTime = currentDateTime() #?mandatory
        resp._market._marketId = marketId
        resp._market._marketStatus = "ACTIVE" #?types:MarketStatusEnum mandatory
        resp._market._marketSuspendTime = currentDateTime() #?mandatory
        resp._market._marketTime = currentDateTime() #?mandatory
        resp._market._marketType = "NOT_APPLICABLE" #?types:MarketTypeEnum mandatory
        resp._market._marketTypeVariant = "D" #?types:MarketTypeVariantEnum mandatory
        resp._market._name = "xsd:string" #optional
        resp._market._numberOfWinners = 1 #mandatory
        resp._market._parentEventId = 1 #mandatory
        resp._market._runnersMayBeAdded = False #?
        resp._market._licenceId = 1 #mandatory
        resp._market._bspMarket = False #mandatory
        
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response



def getMarketPrices(soapBinding, typeDefinition, request, response):
    resp = bfe.GetMarketPricesResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        marketId = request._request._marketId
        resp._marketPrices = bfe.MarketPrices_Def(soapBinding, typeDefinition)
        resp._marketPrices._currencyCode = "GBP"# <xsd:element name="currencyCode" nillable="true" type="xsd:string"/>
        resp._marketPrices._delay = 11111# <xsd:element name="delay" nillable="false" type="xsd:int"/>
        resp._marketPrices._discountAllowed = False# <xsd:element name="discountAllowed" nillable="false" type="xsd:boolean"/>
        resp._marketPrices._lastRefresh = 11111# <xsd:element name="lastRefresh" type="xsd:long"/>
        resp._marketPrices._marketBaseRate = 1.0# <xsd:element name="marketBaseRate" type="xsd:float"/>
        resp._marketPrices._marketId = marketId# <xsd:element name="marketId" nillable="false" type="xsd:int"/>
        resp._marketPrices._marketInfo = None# <xsd:element name="marketInfo" nillable="true" type="xsd:string"/>
        resp._marketPrices._removedRunners = None# <xsd:element name="removedRunners" nillable="true" type="xsd:string"/>
        resp._marketPrices._marketStatus = "ACTIVE"# <xsd:element name="marketStatus" type="types:MarketStatusEnum"/>
        resp._marketPrices._numberOfWinners = 1# <xsd:element name="numberOfWinners" nillable="false" type="xsd:int"/>
        resp._marketPrices._bspMarket = False# <xsd:element name="bspMarket" nillable="false" type="xsd:boolean"/>          
        resp._marketPrices._runnerPrices = None# <xsd:element name="runnerPrices" nillable="true" type="types:ArrayOfRunnerPrices"/>
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def getMarketPricesCompressed(soapBinding, typeDefinition, request, response):
    resp = bfe.GetMarketPricesCompressedResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        resp._marketPrices = "COMPRESSED_STRING"
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def getMarketTradedVolume(soapBinding, typeDefinition, request, response):
    resp = bfe.GetMarketTradedVolumeResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        resp._priceItems = bfe.ArrayOfVolumeInfo_Def(soapBinding, typeDefinition)
        resp._priceItems._VolumeInfo = []

    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def getMarketTradedVolumeCompressed(soapBinding, typeDefinition, request, response):
    resp = bfe.GetMarketTradedVolumeCompressedResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        resp._tradedVolume = '<xsd:element name="tradedVolume" nillable="true" type="xsd:string"/>'
        resp._currencyCode = '<xsd:element name="currencyCode" nillable="true" type="xsd:string"/>'
        resp._marketId = 0 # <xsd:element name="marketId" nillable="false" type="xsd:int"/>
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def updateBets(soapBinding, typeDefinition, request, response):
    resp = bfe.UpdateBetsResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        resp._betResults = bfe.ArrayOfUpdateBetsResult_Def(soapBinding, typeDefinition)
        resp._betResults._UpdateBetsResult = []
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def getMUBets(soapBinding, typeDefinition, request, response):
    resp = bfe.GetMUBetsResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        resp._bets = bfe.ArrayOfBet_Def(soapBinding, typeDefinition)
        resp._bets._Bet = []
        resp._totalRecordCount = len(resp._bets._Bet) # '<xsd:element name="totalRecordCount" nillable="false" type="xsd:int"/>
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def getBet(soapBinding, typeDefinition, request, response):
    resp = bfe.GetBetResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        resp._bet = None # bfe.Bet_Def(soapBinding, typeDefinition)
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def getAllMarkets(soapBinding, typeDefinition, request, response):
    resp = bfe.GetAllMarketsResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        resp._marketData = '<xsd:element name="marketData" nillable="true" type="xsd:string"/>'
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def getBetHistory(soapBinding, typeDefinition, request, response):
    resp = bfe.GetBetHistoryResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        resp._betHistoryItems = bfe.ArrayOfBet_Def(soapBinding, typeDefinition)
        resp._betHistoryItems._Bet = []
    resp._totalRecordCount = len(resp._betHistoryItems._Bet)
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def getInPlayMarkets(soapBinding, typeDefinition, request, response):
    resp = bfe.GetInPlayMarketsResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        resp._marketData = '<xsd:element name="marketData" nillable="true" type="xsd:string"/>'
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response

def getAccountStatement(soapBinding, typeDefinition, request, response):
    resp = bfe.getAccountStatementResp_Def(soapBinding, typeDefinition)
    sessionToken = addHeaderToResponseAndValidateSession(request, resp, soapBinding, typeDefinition)

    if sessionToken:
        resp._items = bfe.ArrayOfAccountStatementItem_Def(soapBinding, typeDefinition)
        resp._items._AccountStatementItem = []
    resp._errorCode = ERROR_CODE_OK
    response._Result = resp
    return response