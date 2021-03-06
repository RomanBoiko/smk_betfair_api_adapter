from __future__ import unicode_literals

import logging
from lxml import etree
import os
import urllib2
import datetime

from jinja2 import Template

from business_layer import BusinessUnit
import smk_api

ERROR_CODE_OK = "OK"
ERROR_INVALID_USERNAME_OR_PASSWORD = "INVALID_USERNAME_OR_PASSWORD"
ERROR_NO_SESSION = "NO_SESSION"
ERROR_API_ERROR = "API_ERROR"
ERROR_CANNOT_ACCEPT_BET = "CANNOT_ACCEPT_BET"
ERROR_BET_NOT_CANCELLED = "BET_NOT_CANCELLED"
ERROR_INVALID_MARKET = "INVALID_MARKET"

BUSINESS_UNIT = BusinessUnit()
LOG = logging.getLogger('[betfair.api]')

def businessUnit():
    return BUSINESS_UNIT

def readFile(path):
    fileStream = urllib2.urlopen("file://%s"%os.path.abspath(path))
    data = fileStream.read()
    fileStream.close()
    return data

actions = {"login": lambda x:login(x),
           "keepAlive": lambda x:keepAlive(x),
           "getAllEventTypes": lambda x:getAllEventTypes(x),
           "getEvents": lambda x:getEvents(x),
           "logout": lambda x:logout(x),
           "getAccountFunds": lambda x:getAccountFunds(x),
           "getCurrentBets": lambda x: getCurrentBets(x),
           "placeBets": lambda x: placeBets(x),
           "cancelBets": lambda x: cancelBets(x),
           "getMarketPricesCompressed": lambda x: getMarketPricesCompressed(x),
           "getAllMarkets": lambda x: getAllMarkets(x),
           "getMarket": lambda x: getMarket(x),
           "cancelBetsByMarket": lambda x: cancelBetsByMarket(x),
           "getMUBets": lambda x: getMUBets(x),
           "getBet": lambda x: getBet(x)}

class BetfairRequest(object):
    def __init__(self, request):
        self.requestTree = etree.XML(request)

    def actionName(self):
        return self.requestTree.xpath("local-name(//*[local-name()='Body']/*[1])")

    def sessionId(self):
        return self.requestTree.xpath("//*[local-name()='sessionToken']/text()")[0]

    def xpath(self, xpathValue):
        return self.requestTree.xpath(xpathValue)\

def dispatchRequest(request):
    betfairRequest = BetfairRequest(request)
    requestType = betfairRequest.actionName()
    action = actions.get(requestType)
    if action is not None:
        return action(betfairRequest)
    else:
        errorMessage = "request type %s could not be dispatched"%requestType
        LOG.error(errorMessage)
        return errorMessage

def login(request):
    username = request.xpath("//*[local-name()='username']/text()")[0]
    password = request.xpath("//*[local-name()='password']/text()")[0]
    template = Template(readFile("templates/login.response.xml"))

    loginResult = businessUnit().authenticateUserAndReturnHisSessionToken(username, password)
    if loginResult.succeeded :
        sessionToken = loginResult.result
        accountStatus = businessUnit().getAccountFunds(sessionToken)
        currency = accountStatus.currency
        return template.render(sessionId=sessionToken, errorCode=ERROR_CODE_OK, currency=currency)
    else:
        return template.render(sessionId="", errorCode=ERROR_INVALID_USERNAME_OR_PASSWORD, currency="")

def keepAlive(request):
    sessionId = request.sessionId()
    template = Template(readFile("templates/keepAlive.response.xml"))
    return template.render(sessionId=sessionId)

def getAllEventTypes(request):
    sessionId = request.sessionId()
    events = businessUnit().getTodaysFootballEvents(sessionId)
    template = Template(readFile("templates/getAllEventTypes.response.xml"))
    return template.render(sessionId=sessionId, eventTypeName="Football", eventTypeId=str(events.footballEventTypeId))

def getEvents(request):
    sessionId = request.sessionId()
    parentId = request.xpath("//*[local-name()='eventParentId']/text()")[0]
    events = businessUnit().getTodaysFootballEvents(sessionId)
    template = Template(readFile("templates/getEvents.response.xml"))
    if str(parentId) in events.parentToEvent:
        return template.render(sessionId=sessionId, events=events.parentToEvent[str(parentId)], markets=[], parentId=parentId)
    elif str(parentId) in events.eventToMarket:
        return template.render(sessionId=sessionId, events=[], markets=events.eventToMarket[str(parentId)], parentId=parentId)
    else:
        return template.render(sessionId=sessionId, events=[], markets=[], parentId=parentId)

def logout(request):
    sessionId = request.sessionId()
    logoutActionResult = businessUnit().logUserOutAndReturnResultOfAction(sessionId)
    if logoutActionResult:
        errorCode = ERROR_CODE_OK
    else:
        errorCode = ERROR_API_ERROR
    return Template(readFile("templates/logout.response.xml")).render(errorCode=errorCode)

def getAccountFunds(request):
    sessionId = request.sessionId()
    getAccountFundsResult = businessUnit().getAccountFunds(sessionId)
    return Template(readFile("templates/getAccountFunds.response.xml")).render(sessionId=sessionId, funds=getAccountFundsResult)

def getCurrentBets(request):
    sessionId = request.sessionId()
    currentBets = businessUnit().getBetsForAccount(sessionId)
    return Template(readFile("templates/getCurrentBets.response.xml")).render(sessionId=sessionId, bets=currentBets.bets)

def placeBets(request):
    sessionId = request.sessionId()
    placeBets = request.xpath("//*[local-name()='PlaceBets']")
    betResults = []
    for bet in placeBets:
        betType = bet.find('betType').text
        marketId = int(bet.find('marketId').text)
        contractId = int(bet.find('selectionId').text)
        sizeInPounds = float(bet.find('size').text)
        priceInBetfairFormatBetween1and1000 = int(bet.find('price').text)
        isBetTypeBuy = ("B" == betType)
        betResult = businessUnit().placeBet(sessionId, marketId, contractId, sizeInPounds, priceInBetfairFormatBetween1and1000, isBetTypeBuy)
        betResults.append(betResult)
    return Template(readFile("templates/placeBets.response.xml")).render(sessionId=sessionId, bets=betResults)

def cancelBets(request):
    sessionId = request.sessionId()
    cancelBets = request.xpath("//*[local-name()='CancelBets']")
    betResults = []
    for bet in cancelBets:
        betId = bet.find('betId').text
        betResults.append(businessUnit().cancelBet(sessionId, int(betId)))
    return Template(readFile("templates/cancelBets.response.xml")).render(sessionId=sessionId, bets=betResults)

def getAllMarkets(request):
    sessionId = request.sessionId()
    events = businessUnit().getTodaysFootballEvents(sessionId)
    resultsTildaSeparated = []
    for market in events.marketIdToMarket.values():
        marketData = [market.marketId, market.marketName, market.marketTypeId,# or 'A', type?
            'ACTIVE', (int(market.startTime.strftime("%s")) * 1000),
            'Football\\%s'%market.marketName, 'eventHierarchy',
            0,#betDelay
            1,#exchangeId
            '',#ISO of country to host event, empty for international
            (int(datetime.datetime.now().strftime("%s")) * 1000),
            0,#numberOfRunners
            0,#numberOfPossibleWinners in the market
            0.0,#TotalAmountMatched
            'N',#Non-BSP market(BetfairStartingPrice)
            'Y'#Scheduled to be turned in-play
            ]
        marketDataCompressed = "~".join('%s' % m for m in marketData)
        resultsTildaSeparated.append(marketDataCompressed)
    result = ":".join(resultsTildaSeparated)
    result = result.replace("&", "&amp;")
    return Template(readFile("templates/getAllMarkets.response.xml")).render(sessionId=sessionId, marketsData=result)

def getMarket(request):
    sessionId = request.sessionId()
    marketId = int(request.xpath("//*[local-name()='marketId']/text()")[0])
    events = businessUnit().getTodaysFootballEvents(sessionId)
    market = events.marketIdToMarket.get(str(marketId))
    contracts = events.marketToContract.get(str(marketId))
    return Template(readFile("templates/getMarket.response.xml")).render(sessionId=sessionId, market=market, contracts=contracts)

def getMarketPricesCompressed(request):
    sessionId = request.sessionId()
    marketId = int(request.xpath("//*[local-name()='marketId']/text()")[0])
    getPricesResult = businessUnit().getMarketPrices(sessionId, marketId)
    responseTemplate = Template(readFile("templates/getMarketPricesCompressed.response.xml"))
    if getPricesResult.succeeded:
        return responseTemplate.render(sessionId=sessionId, errorCode="OK", marketPricesCompressed=MarketPrices(getPricesResult.result).compress())
    else:
        return responseTemplate.render(sessionId=sessionId, errorCode="INVALID_MARKET", marketPricesCompressed="")
    
def cancelBetsByMarket(request):
    sessionId = request.sessionId()
    marketsToCancel = request.xpath("//*[local-name()='int']/text()")
    cancelResults = []
    betsForAccount = businessUnit().getBetsForAccount(sessionId)
    for marketIdToCancel in marketsToCancel:
        for betDetails in betsForAccount.bets:
            if betDetails.marketId == int(marketIdToCancel):
                businessUnit().cancelBet(sessionId, betDetails.id)
        cancelResults.append(marketIdToCancel)#append also status of cancel
    return Template(readFile("templates/cancelBetsByMarket.response.xml")).render(sessionId=sessionId, cancelResults=cancelResults)

def getMUBets(request):
    sessionId = request.sessionId()
    
    marketId = int(request.xpath("//*[local-name()='marketId']/text()")[0])
    betStatus = request.xpath("//*[local-name()='betStatus']/text()")[0]

    betsForAccount = businessUnit().getBetsForAccount(sessionId)
    muBets = []
    for betDetails in betsForAccount.bets:
        if betDetails.marketId==marketId and betDetails.status==betStatus:
            muBets.append(betDetails)
    return Template(readFile("templates/getMUBets.response.xml")).render(sessionId=sessionId, bets=muBets, totalRecordCount=len(muBets))

def getBet(request):
    sessionId = request.sessionId()
    
    betId = int(request.xpath("//*[local-name()='betId']/text()")[0])

    betsForAccount = businessUnit().getBetsForAccount(sessionId)
    betToReturn = None
    for betDetails in betsForAccount.bets:
        if betDetails.id==betId:
            betToReturn = betDetails
    return Template(readFile("templates/getBet.response.xml")).render(sessionId=sessionId, bet=betToReturn)

class MarketPrices(object):
    def __init__(self, smkMarketPrices):
        self.smkMarketPrices = smkMarketPrices
        self.currency = "GBP"
        self.marketStatus = "ACTIVE"
        self.inPlayDelay = 0
        self.numberOfWinners = 1
        self.marketInformation = None
        self.isDiscountAllowed = "false"
        self.marketBaseRate = 0.0#Base rate of commission on market
        self.refreshTimeInMilliseconds = 0#deprecated
        self.removedRunnersInformationComposed = ""#should be three fields per each removed runner
        self.bspMarket="N"

    def compress(self):
        priceDepth=1#Hardcoded, to implement ordering by price!
        contractsOrRunners = []
        for contract in self.smkMarketPrices.contracts:
            contractDetails = str(contract.contractId)+"~0~0.0~0.0~~0.0~false~0.0~0.0~0.0"
            backPricesStrings = []
            for price in contract.bids:
                backPricesStrings.append("~".join([str(price.price),str(price.quantity), "B", str(priceDepth) ]))
            backPricesCompressed = "~".join(backPricesStrings)
    
            layPricesStrings = []
            for price in contract.offers:
                layPricesStrings.append("~".join([str(price.price),str(price.quantity), "L", str(priceDepth) ]))
            layPricesCompressed = "~".join(layPricesStrings)
            
            contractsOrRunners.append("|".join([contractDetails, layPricesCompressed, backPricesCompressed]))

        marketDetailsCompressed = "~".join(map(str, [self.smkMarketPrices.marketId, self.currency, self.marketStatus,self.inPlayDelay, self.numberOfWinners, self.marketInformation,
            self.isDiscountAllowed, self.marketBaseRate, self.refreshTimeInMilliseconds, self.removedRunnersInformationComposed, self.bspMarket]))
        if len(contractsOrRunners) == 0:
            return marketDetailsCompressed
        else:
            contractsOrRunnersCompressed = ":".join(contractsOrRunners)
            return marketDetailsCompressed + ":" + contractsOrRunnersCompressed
