import logging

from google.protobuf import text_format

import smarkets
import smarkets.seto.piqi_pb2 as seto
from smarkets.uuid import Uuid, uuid_to_int

import adapter_context

LOGGER = logging.getLogger('[smk.api]')
FOOTBALL_EVENT_TYPE_ID = 121005

class AccountState(object):
    def __init__(self, accountStateMessage):
        self.id=uuidToInteger(accountStateMessage.account_state.account)
        self.currency=accountStateMessage.account_state.currency
        self.cash=accountStateMessage.account_state.cash.value
        self.bonus=accountStateMessage.account_state.bonus.value#do we need that?
        self.exposure=accountStateMessage.account_state.exposure.value#do we need that?
    
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
        self.id=111
    def __str__(self):
        return ("BetCancel(id=%s)"%(self.id))
    def __repr__(self):
        return self.__str__()

class BetsForAccount(object):
    def __init__(self, ordersForAccountMessage):
        self.markets = []
        for marketOrders in ordersForAccountMessage.orders_for_account.markets:
            self.markets.append(uuidToInteger(marketOrders.market))
    def __str__(self):
        return ("BetsForAccount(id=%s)"%(len(self.markets)))
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

class Event(object):
    def __init__(self, eventId, eventName, eventTypeId):
        self.eventId = eventId
        self.eventName = eventName
        self.eventTypeId = eventTypeId

    def __str__(self):
        return ("Event(id=%s, name=%s, typeId=%s)"%(self.eventId, self.eventName.encode("utf-8"), self.eventTypeId))
    def __repr__(self):
        return self.__str__()

#unused
class Market(object):
    def __init__(self, marketId, marketName, marketTypeId, marketParentEventId):
        self.marketId = marketId
        self.marketName = marketName
        self.marketTypeId = marketTypeId
        self.marketParentEventId = marketParentEventId

def uuidToInteger(uuid):
    uu = Uuid.from_int((uuid.high, uuid.low), 'Account')
    return uuid_to_int(uu.to_hex())

def integerToUuid(sourceInt):
    sourceUuid = Uuid.from_int(sourceInt, 'Account')
    resultedUuid = seto.Uuid128()
    resultedUuid.low = sourceUuid.low
    resultedUuid.high = sourceUuid.high
    return resultedUuid

def login(username, password):
    settings = smarkets.SessionSettings(username, password)
    settings.host = adapter_context.SMK_API_HOST
    settings.port = int(adapter_context.SMK_API_PORT)
    session = smarkets.Session(settings)
    client = smarkets.Smarkets(session)
    client.login()
    client.ping()
    client.flush()
    client.read()
    return SmkClient(client) 

    
def loadEvents(eventsMessage):
    events = Events()
    footballEvent = lambda eventId, eventName: Event(eventId, eventName, FOOTBALL_EVENT_TYPE_ID)
    
    if eventsMessage is not None:
        for parent in eventsMessage.parents:
            parentIdInt = uuidToInteger(parent.event)
            if parentIdInt!=FOOTBALL_EVENT_TYPE_ID :
                events.putEvent(FOOTBALL_EVENT_TYPE_ID, footballEvent(parentIdInt, parent.name))
        for sportEvent in eventsMessage.with_markets:
            eventIdInt = uuidToInteger(sportEvent.event)
            parentIdInt = uuidToInteger(sportEvent.parent)
            events.putEvent(parentIdInt, footballEvent(eventIdInt, sportEvent.name))

            for marketItem in sportEvent.markets :
                marketIdInt = uuidToInteger(marketItem.market)
                events.putEvent(eventIdInt, footballEvent(marketIdInt, marketItem.name))
                for contract in marketItem.contracts :
                    smkContract = Market(uuidToInteger(contract.contract),
                                         contract.name,
                                         FOOTBALL_EVENT_TYPE_ID,
                                         marketIdInt)
                    events.putContract(marketIdInt, smkContract)
    return events

class SmkClient(object):
    LOGGER = logging.getLogger('[smk.client]')
    def __init__(self, client):
        self.client = client
        self.smkResponsePayload = None
        
    def getClient(self):
        return self.client
    def logout(self):
        self.client.logout()
        
    def dataHandlingCallback(self, message):
        self.smkResponsePayload = message
        
    def getSmkResponse(self, clientAction, expectedResponseType, classToConstruct):
        self.smkResponsePayload = None
        callback = lambda message: self.dataHandlingCallback(message)
        self.client.add_handler(expectedResponseType, callback)
        clientAction()
        self.client.flush()

        while self.smkResponsePayload is None:
            self.client.read()
            self.client.flush()
        self.client.del_handler(expectedResponseType, callback)
        return classToConstruct(self.smkResponsePayload)
    
    def getAccountState(self):
        return self.getSmkResponse(lambda: self.client.request_account_state(), 'seto.account_state', AccountState)

    def getBetsForAccount(self):
        return self.getSmkResponse(lambda: self.client.request_orders_for_account(), 'seto.orders_for_account', BetsForAccount)

    def placeBet(self, marketId, contractId, quantity, price):
        order = smarkets.Order()
        order.quantity = quantity#pounds*10000
        order.price = price#procents*100
        order.side = smarkets.Order.BUY
        
        order.market = integerToUuid(marketId)
        order.contract = integerToUuid(contractId)
        
        return self.getSmkResponse(lambda: self.client.order(order), 'seto.order_accepted', Bet)#add nonsuccessful case:seto.order_rejected

    def cancelBet(self, orderId):
        order = integerToUuid(orderId)
        return self.getSmkResponse(lambda: self.client.order_cancel(order), 'seto.order_cancelled', BetCancel)#add nonsuccessful case:seto.order_rejected
    
    def getPayloadViaHttp(self, serviceUrl):
        content_type, result = smarkets.urls.fetch(serviceUrl)
        if content_type == 'application/x-protobuf':
            incoming_payload = seto.Events()
            incoming_payload.ParseFromString(result)
            self.LOGGER.debug("Response from %s: %s"%(serviceUrl, text_format.MessageToString(incoming_payload)))
            return incoming_payload
        return "return nothing - fix"

    def getEvents(self, eventRequest):
        httpUrl = self.getSmkResponse(lambda: self.client.request_events(eventRequest), 'seto.http_found', HttpUrl)
        return self.getPayloadViaHttp(httpUrl.url)
    
    def footballByDate(self, eventsDate):
        eventsMessage = self.getEvents(smarkets.events.FootballByDate(eventsDate))
        return loadEvents(eventsMessage)
