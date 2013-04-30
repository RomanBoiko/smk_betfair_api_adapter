import logging
from lxml import etree
import os
import urllib2

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

def unicodeXml(xml):
    return bytes(bytearray(xml, encoding='utf-8'))

actions = {"login": lambda x:login(x),
           "getAllEventTypes": lambda x:getAllEventTypes(x),
           "logout": lambda x:logout(x),
           "getAccountFunds": lambda x:getAccountFunds(x),
           "getCurrentBets": lambda x: getCurrentBets(x),
           "placeBets": lambda x: placeBets(x),
           "cancelBets": lambda x: cancelBets(x),
           "getMarketPricesCompressed": lambda x: getMarketPricesCompressed(x),
           "getAllMarkets": lambda x: getAllMarkets(x)}

class BetfairRequest(object):
    def __init__(self, request):
        self.requestTree = etree.XML(unicodeXml(request))

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

def getAllEventTypes(request):
    sessionId = request.sessionId()
    template = Template(readFile("templates/getAllEventTypes.response.xml"))
    return template.render(sessionId=sessionId, eventTypeName="Football", eventTypeId=str(smk_api.FOOTBALL_EVENT_TYPE_ID))

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
        marketData = [market.eventId, market.eventName, market.eventTypeId,# or 'A', type?
            'ACTIVE', (int(market.startTime.strftime("%s")) * 1000),
            'menuPath', 'eventHierarchy', 'betDelay', 1,#exchangeId
            ''#ISO of country to host event, empty for international
            'lastRefresh',
            2,#numberOfRunners
            1,#numberOfPossibleWinners in the market
            0.0,#TotalAmountMatched
            'N',#Non-BSP market(BetfairStartingPrice)
            'Y'#Scheduled to be turned in-play
            ]
        resultsTildaSeparated.append("~".join(map(str, marketData)))
    result = ":".join(resultsTildaSeparated)
    return Template(readFile("templates/getAllMarkets.response.xml")).render(sessionId=sessionId, marketsData=result)

def getMarketPricesCompressed(request):
    sessionId = request.sessionId()
    marketId = int(request.xpath("//*[local-name()='marketId']/text()")[0])
    getPricesResult = businessUnit().getMarketPrices(sessionId, marketId)
    responseTemplate = Template(readFile("templates/getMarketPricesCompressed.response.xml"))
    if getPricesResult.succeeded:
        return responseTemplate.render(sessionId=sessionId, errorCode="OK", marketPricesCompressed=MarketPrices(getPricesResult.result).compress())
    else:
        return responseTemplate.render(sessionId=sessionId, errorCode="INVALID_MARKET", marketPricesCompressed="")
    

class MarketPrice(object):
    def __init__(self, price, amount, oposingTypeToBeMatchedAgainst):
        self.price = price
        self.amount = amount
        self.oposingTypeToBeMatchedAgainst = oposingTypeToBeMatchedAgainst
        self.depth = 1#to implement ordering by price!

class BackPrice(MarketPrice):
    def __init__(self, price, amount):
        super(BackPrice, self).__init__(price, amount, 'L')

class LayPrice(MarketPrice):
    def __init__(self, price, amount):
        super(LayPrice, self).__init__(price, amount, 'B')
    
class MarketPrices(object):
    def __init__(self, smkMarketPrices):
        self.marketId = smkMarketPrices.marketId
        self.currency = "GBP"#???
        self.marketStatus = "ACTIVE"#???putCorrect
        self.inPlayDelay = 0#??
        self.numberOfWinners = 1#??
        self.marketInformation = None#nullable
        self.isDiscountAllowed = False
        self.marketBaseRate = 0.0#"comission"#Base rate of commission on market
        self.refreshTimeInMilliseconds = 0#deprecated
        self.removedRunnersInformationComposed = ""#should be three fields per each removed runner
        self.bspMarket="N"
        self.runnerInformationFields = ""#info per runner
        self.backPrices = []
        for smkBid in smkMarketPrices.bids:
            self.backPrices.append(BackPrice(smkBid.price, smkBid.quantity))
        self.layPrices = []
        for smkOffer in smkMarketPrices.offers:
            self.layPrices.append(LayPrice(smkOffer.price, smkOffer.quantity))

    def compress(self):
        backPricesStrings = []
        for price in self.backPrices:
            backPricesStrings.append("|".join([str(price.price),str(price.amount), price.oposingTypeToBeMatchedAgainst, str(price.depth) ]))
        backPricesCompressed = "|".join(backPricesStrings)

        layPricesStrings = []
        for price in self.layPrices:
            layPricesStrings.append("|".join([str(price.price),str(price.amount), price.oposingTypeToBeMatchedAgainst, str(price.depth) ]))
        layPricesCompressed = "|".join(layPricesStrings)

        return "~".join(map(str, [self.marketId, self.currency, self.marketStatus,self.inPlayDelay, self.numberOfWinners, self.marketInformation,
            self.isDiscountAllowed, self.marketBaseRate, self.refreshTimeInMilliseconds, self.removedRunnersInformationComposed,
            self.bspMarket, self.runnerInformationFields, backPricesCompressed, layPricesCompressed]))