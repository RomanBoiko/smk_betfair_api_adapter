import logging
import threading
import time
import pprint
from xmlrpclib import datetime
from datetime import timedelta

from google.protobuf import text_format

import smarkets
import smarkets.seto.piqi_pb2 as seto
from smarkets.uuid import Uuid, uuid_to_int
from smarkets.exceptions import SocketDisconnected

import adapter_context

LOGGER = logging.getLogger('[smk.api]')
FOOTBALL_EVENT_TYPE_ID = 121005
SMK_CASH_MULTIPLIER = 10000

FOOTBALL_EVENTS_AVAILABILITY_IN_FUTURE_DAYS = 6

def smkCashAmountToReal(smkCashAmount):
    return float(smkCashAmount)/SMK_CASH_MULTIPLIER

def realCashAmountToSmk(realCashAmount):
    return int(round(realCashAmount*SMK_CASH_MULTIPLIER))

def extractCurrencyFromAccountStateMessage(currencyCode):
    for currency in seto._CURRENCY.values:
        if currency.number == currencyCode:
            return (str(currency.name))[-3:]
    raise Exception("CURRENCY NOT RECOGNISED(%s)"%str(currencyCode))

def orderStatusCodeToString(orderStatusCode):
    for statusCode in seto._ORDERSTATUS.values:
        if statusCode.number == orderStatusCode:
            return (str(statusCode.name))[len("ORDER_STATUS_"):]
    raise Exception("ORDER_STATUS_CODE NOT RECOGNISED(%s)"%str(currencyCode))


class AccountState(object):
    def __init__(self, accountStateMessage):
        self.id=uuidToInteger(accountStateMessage.account_state.account)
        self.currency= extractCurrencyFromAccountStateMessage(accountStateMessage.account_state.currency)
        self.cash=smkCashAmountToReal(accountStateMessage.account_state.cash.value)
        self.bonus=smkCashAmountToReal(accountStateMessage.account_state.bonus.value)#do we need that?
        self.exposure=smkCashAmountToReal(accountStateMessage.account_state.exposure.value)#do we need that?
    
    def __str__(self):
        return ("AccountState(id=%s, currency=%s, cash=%s, bonus=%s, exposure=%s)"%(self.id, self.currency, self.cash, self.bonus, self.exposure))
    def __repr__(self):
        return self.__str__()

class Bet(object):
    def __init__(self, orderAcceptedMessage):
        self.id=uuidToInteger(orderAcceptedMessage.order_accepted.order)
    def __str__(self):
        return ("Bet(id=%s)"%(self.id))
    def __repr__(self):
        return self.__str__()

class BetCancel(object):
    def __init__(self, betCancelMessage):
        self.id=uuidToInteger(betCancelMessage.order_cancelled.order)
    def __str__(self):
        return ("BetCancel(id=%s)"%(self.id))
    def __repr__(self):
        return self.__str__()

class BetDetails(object):
    def __init__(self, id, marketId, contractId, price, status, quantity, createdDateInMillis, isBetTypeBuy):
        self.id = id
        self.marketId = marketId
        self.contractId = contractId
        self.price = price
        self.status = orderStatusCodeToString(status)
        self.quantity = quantity
        self.createdDateInMillis = createdDateInMillis
        self.isBetTypeBuy = isBetTypeBuy
    def __str__(self):
        return ("BetDetails(id=%s, market=%s, contractId=%s, price=%s, status=%s, quantity=%s, createdDateInMillis=%s, isBetTypeBuy=%s)"%(self.id, self.marketId, self.contractId, self.price, self.status, self.quantity, self.createdDateInMillis, self.isBetTypeBuy))
    def __repr__(self):
        return self.__str__()

class BetsForAccount(object):
    def __init__(self, ordersForAccountMessage):
        self.bets = []
        for marketOrders in ordersForAccountMessage.orders_for_account.markets:
            marketId = uuidToInteger(marketOrders.market)
            for contract in marketOrders.contracts:
                contractId = uuidToInteger(contract.contract)
                for bid in contract.bids:
                    price = bid.price
                    for order in bid.orders:
                        orderId = uuidToInteger(order.order)
                        status = order.status
                        quantity = order.quantity
                        createdDateInMillis = order.created_microseconds
                        self.bets.append(BetDetails(orderId, marketId, contractId, price, status, quantity, createdDateInMillis, True))
                for bid in contract.offers:
                    price = bid.price
                    for order in bid.orders:
                        orderId = uuidToInteger(order.order)
                        status = order.status
                        quantity = order.quantity
                        createdDateInMillis = order.created_microseconds
                        self.bets.append(BetDetails(orderId, marketId, contractId, price, status, quantity, createdDateInMillis, False))
    def __str__(self):
        return ("BetsForAccount(bets=%s)"%(pprint.pformat(self.bets)))
    def __repr__(self):
        return self.__str__()
    
class HttpUrl(object):
    def __init__(self, httpUrlMessage):
        urlFetched = httpUrlMessage.http_found.url
        normalizedUrl = urlFetched.replace("vagrant-dev.corp", "api-sandbox")
        self.url = normalizedUrl

class Events(object):
    def __init__(self):
        self.parentToEvent={}
        self.marketToContract={}
    def putEvent(self, parentIdInt, event):
        if str(parentIdInt) not in self.parentToEvent:
            self.parentToEvent[str(parentIdInt)] = []
        self.parentToEvent[str(parentIdInt)].append(event)
    def putContract(self, parentMarketIdInt, contract):
        if str(parentMarketIdInt) not in self.marketToContract:
            self.marketToContract[str(parentMarketIdInt)] = []
        self.marketToContract[str(parentMarketIdInt)].append(contract)

    def parentsCount(self):
        return len(self.parentToEvent)
    def eventsAndMarketsCount(self):
        eventsAndMarketsCount = 0
        for parent in self.parentToEvent:
            eventsAndMarketsCount += len(self.parentToEvent[parent])
        return eventsAndMarketsCount
    def marketsCount(self):
        return len(self.marketToContract)
    def contractsCount(self):
        contractsCount = 0
        for market in self.marketToContract:
            contractsCount += len(self.marketToContract[market])
        return contractsCount


class Event(object):
    def __init__(self, eventId, eventName, eventTypeId, startDateTime):
        self.eventId = eventId
        self.eventName = eventName
        self.eventTypeId = eventTypeId
        self.startTime = startDateTime

    def __str__(self):
        return ("Event(id=%s, name=%s, typeId=%s)"%(self.eventId, self.eventName.encode("utf-8"), self.eventTypeId))
    def __repr__(self):
        return self.__str__()

class Market(object):
    def __init__(self, marketId, marketName, marketTypeId, marketParentEventId, startDateTime):
        self.marketId = marketId
        self.marketName = marketName
        self.marketTypeId = marketTypeId
        self.marketParentEventId = marketParentEventId
        self.startTime = startDateTime

def uuidToInteger(uuid):
    uu = Uuid.from_int((uuid.high, uuid.low), 'Account')
    return uuid_to_int(uu.to_hex())

def integerToUuid(sourceInt):
    sourceUuid = Uuid.from_int(sourceInt, 'Account')
    resultedUuid = seto.Uuid128()
    resultedUuid.low = sourceUuid.low
    resultedUuid.high = sourceUuid.high
    return resultedUuid


class EventsParser(object):

    def __init__(self):
        self._events = None

    def footballEvent(self, eventId, eventName, startDateTime):
        return Event(eventId, eventName, FOOTBALL_EVENT_TYPE_ID, startDateTime)

    def dateTime(self, year=1970, month=1, day=1, hour=0, minute=0):
        return list(datetime.datetime(year, month, day, hour, minute).timetuple())

    def addParentEvent(self, parent):
        parentIdInt = uuidToInteger(parent.event)
        if parentIdInt!=FOOTBALL_EVENT_TYPE_ID :
            eventStartTime = self.dateTime(parent.start_date.year, parent.start_date.month, parent.start_date.day)
            self._events.putEvent(FOOTBALL_EVENT_TYPE_ID, self.footballEvent(parentIdInt, parent.name, eventStartTime))

    def addContract(self, contract, marketIdInt, eventStartTime):
        smkContract = Market(uuidToInteger(contract.contract),
                             contract.name,
                             FOOTBALL_EVENT_TYPE_ID,
                             marketIdInt, eventStartTime)
        self._events.putContract(marketIdInt, smkContract)

    def addMarket(self, marketItem, eventIdInt, eventStartTime):
        marketIdInt = uuidToInteger(marketItem.market)
        self._events.putEvent(eventIdInt, self.footballEvent(marketIdInt, marketItem.name, eventStartTime))
        for contract in marketItem.contracts :
            self.addContract(contract, marketIdInt, eventStartTime)

    def addEvent(self, sportEvent):
        eventIdInt = uuidToInteger(sportEvent.event)
        parentIdInt = uuidToInteger(sportEvent.parent)
        eventStartTime = self.dateTime(sportEvent.start_date.year, sportEvent.start_date.month, sportEvent.start_date.day, sportEvent.start_time.hour, sportEvent.start_time.minute)
        self._events.putEvent(parentIdInt, self.footballEvent(eventIdInt, sportEvent.name, eventStartTime))

        for marketItem in sportEvent.markets :
            self.addMarket(marketItem, eventIdInt, eventStartTime)

    def parseEvents(self, eventsMessages):
        self._events = Events()
        for eventsMessage in eventsMessages:
            if eventsMessage is not None:
                for parent in eventsMessage.parents:
                    self.addParentEvent(parent)
                for sportEvent in eventsMessage.with_markets:
                    self.addEvent(sportEvent)
        return self._events

class ActionResult(object):
    def __init__(self, hasSucceeded, result):
        self.succeeded = hasSucceeded
        self.result = result

class ActionSucceeded(ActionResult):
    def __init__(self, result):
        super(ActionSucceeded, self).__init__(True, result)
class ActionFailed(ActionResult):
    def __init__(self, result):
        super(ActionFailed, self).__init__(False, result)


def login(username, password):
    try:
        settings = smarkets.SessionSettings(username, password)
        settings.host = adapter_context.SMK_API_HOST
        settings.port = int(adapter_context.SMK_API_PORT)
        session = smarkets.Session(settings)
        client = smarkets.Smarkets(session)
        client.login()
        client.ping()
        client.flush()
        client.read()
        return ActionSucceeded(SmkClient(client))
    except SocketDisconnected:
        return ActionFailed("login failed")


def todaysDate():
    return datetime.date.today()

class EventsCache(object):
    def __init__(self):
        self._events = None
        self._cacheCreationDate = None

    def isUpToDate(self):
        return self._cacheCreationDate == todaysDate()

    def updateEvents(self, events):
        self._events = events
        self._cacheCreationDate = todaysDate()

    def getEvents(self):
        return self._events


class SmkClient(object):
    LOGGER = logging.getLogger('[smk.client]')
    
    def __init__(self, client):
        self.smkResponse = None
        self.client = client
        self.clientLock = threading.Lock()
        self.threadStopEvent = threading.Event()
        self.periodicThread = threading.Thread(target=self.periodicalFlush)
        self.periodicThread.daemon = True
        self.periodicThread.start()
        self.footballEventsCache = EventsCache()

    def periodicalFlush(self):
        while not self.threadStopEvent.is_set():
            LOGGER.info("periodicalFlush: wake up")
            self.clientLock.acquire()
            try:
                self.client.read()
                self.client.flush()
            finally:
                self.clientLock.release()
            LOGGER.info("periodicalFlush: go to sleep")
            self.threadStopEvent.wait(10)
        
    def logout(self):
        self.clientLock.acquire()
        try:
            self.threadStopEvent.set()
            self.client.logout()
        finally:
            self.clientLock.release()
        
    def actionSucceeded(self, message):
        self.smkResponse = ActionSucceeded(message)
    def actionFailed(self, message):
        self.smkResponse = ActionFailed(message)
        
    def getSmkResponse(self, clientAction, expectedResponseType, classToConstruct, expectedFailureResponseType=None):
        self.smkResponse = None
        callbackPositive = lambda message: self.actionSucceeded(message)
        callbackNegative = lambda message: self.actionFailed(message)
        callbacks = {expectedResponseType: callbackPositive}
        self.clientLock.acquire()
        try:
            self.client.add_handler(expectedResponseType, callbackPositive)
            if expectedFailureResponseType is not None:
                self.client.add_handler(expectedFailureResponseType, callbackNegative)
                callbacks[expectedFailureResponseType] = callbackNegative

            clientAction()
            self.client.flush()
    
            while self.smkResponse is None:
                self.client.read()
                self.client.flush()
            for callbackType in callbacks :
                self.client.del_handler(callbackType, callbacks[callbackType])
        finally:
            self.clientLock.release()
        if self.smkResponse.succeeded :
            return ActionSucceeded(classToConstruct(self.smkResponse.result))
        else:
            return ActionFailed("failure reason")

    
    def getAccountState(self):
        return self.getSmkResponse(lambda: self.client.request_account_state(), 'seto.account_state', AccountState).result

    def getBetsForAccount(self):
        return self.getSmkResponse(lambda: self.client.request_orders_for_account(), 'seto.orders_for_account', BetsForAccount).result

    def placeBet(self, marketId, contractId, quantity, price, isBetTypeBuy):
        order = smarkets.Order()
        order.quantity = realCashAmountToSmk(quantity)
        order.price = price#procents*100
        if isBetTypeBuy:
            order.side = smarkets.Order.BUY
        else:
            order.side = smarkets.Order.SELL
        order.market = integerToUuid(marketId)
        order.contract = integerToUuid(contractId)
        
        return self.getSmkResponse(lambda: self.client.order(order), 'seto.order_accepted', Bet, 'seto.order_rejected')

    def cancelBet(self, orderId):
        order = integerToUuid(orderId)
        return self.getSmkResponse(lambda: self.client.order_cancel(order), 'seto.order_cancelled', BetCancel, 'seto.order_cancel_rejected')
    
    def getPayloadViaHttp(self, serviceUrl):
        content_type, result = smarkets.urls.fetch(serviceUrl)
        if content_type == 'application/x-protobuf':
            incoming_payload = seto.Events()
            incoming_payload.ParseFromString(result)
            self.LOGGER.debug("Response from %s: %s"%(serviceUrl, text_format.MessageToString(incoming_payload)))
            return incoming_payload
        return "return nothing - fix"

    def getEventsUrls(self, eventRequest):
        httpUrl = self.getSmkResponse(lambda: self.client.request_events(eventRequest), 'seto.http_found', HttpUrl, 'seto.invalid_request')
        if httpUrl.succeeded:
            return httpUrl.result.url
        raise Exception("No events for %s"%eventRequest)

    def footballActiveEvents(self):
        if not self.footballEventsCache.isUpToDate():
            eventsMessages = []
            eventsMessagesUrls = []
            datePlusDelta = lambda daysDelta: (todaysDate()+timedelta(days=daysDelta))
            numberOfDaysToGetEventsFor = 1 if adapter_context.isAdapterRunningInTestContext() else 7
            for dayDelta in range(numberOfDaysToGetEventsFor):
                day = datePlusDelta(dayDelta)
                eventsMessagesUrls.append(self.getEventsUrls(smarkets.events.FootballByDate(day)))
            for eventsUrl in eventsMessagesUrls:
                eventsMessages.append(self.getPayloadViaHttp(eventsUrl))
            self.footballEventsCache.updateEvents(EventsParser().parseEvents(eventsMessages))
        return self.footballEventsCache.getEvents()
