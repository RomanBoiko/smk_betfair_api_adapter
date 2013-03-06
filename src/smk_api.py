import logging

from google.protobuf import text_format

import smarkets
import smarkets.seto.piqi_pb2 as seto
from smarkets.uuid import Uuid, uuid_to_int

import adapter_context

LOGGER = logging.getLogger('[smk.api]')
FOOTBALL_EVENT_TYPE_ID = 121005

def uuid_to_integer(uuid):
    uu = Uuid.from_int((uuid.high, uuid.low), 'Account')
    return uuid_to_int(uu.to_hex())

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
    return client 
    
def logout(client):
    client.logout()
    
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

class EventsBroker():
    LOGGER = logging.getLogger('[events.broker]')

    def __init__(self, client):
        self.eventsMessage = None
        self.client = client
        
    def doWithHttpService(self, serviceUrl):
        content_type, result = smarkets.urls.fetch(serviceUrl)
        if content_type == 'application/x-protobuf':
            incoming_payload = seto.Events()
            incoming_payload.ParseFromString(result)
            self.LOGGER.debug("Response from %s: %s"%(serviceUrl, text_format.MessageToString(incoming_payload)))
            self.eventsMessage = incoming_payload

    def httpDataFetchingCallback(self, message):
        self.LOGGER.debug("Received football event response: %s" % (text_format.MessageToString(message)))
        url = message.http_found.url
        normalizedUrl = url.replace("vagrant-dev.corp", "api-sandbox")
        self.LOGGER.debug("URL to be used for events load: %s" % normalizedUrl)
        self.doWithHttpService(normalizedUrl)
        
    def getEvents(self, eventRequest):
        callback = lambda x: self.httpDataFetchingCallback(x)
        self.client.add_handler('seto.http_found', callback)
        self.client.request_events(eventRequest)
        self.client.flush()
        self.client.read()
        self.client.del_handler('seto.http_found', callback)
        return self.eventsMessage
    
    def footballByDate(self, eventsDate):
        eventsMessage = self.getEvents(smarkets.events.FootballByDate(eventsDate))
        return self.loadEvents(eventsMessage)
    
    def loadEvents(self, eventsMessage):
        events = Events()
        footballEvent = lambda eventId, eventName: Event(eventId, eventName, FOOTBALL_EVENT_TYPE_ID)
        
        for parent in eventsMessage.parents:
            parentIdInt = uuid_to_integer(parent.event)
            if parentIdInt!=FOOTBALL_EVENT_TYPE_ID :
                events.putEvent(FOOTBALL_EVENT_TYPE_ID, footballEvent(parentIdInt, parent.name))
        for sportEvent in eventsMessage.with_markets:
            eventIdInt = uuid_to_integer(sportEvent.event)
            parentIdInt = uuid_to_integer(sportEvent.parent)
            events.putEvent(parentIdInt, footballEvent(eventIdInt, sportEvent.name))

            for marketItem in sportEvent.markets :
                marketIdInt = uuid_to_integer(marketItem.market)
                events.putEvent(eventIdInt, footballEvent(marketIdInt, marketItem.name))
                for contract in marketItem.contracts :
                    smkContract = Market(uuid_to_integer(contract.contract),
                                         contract.name,
                                         FOOTBALL_EVENT_TYPE_ID,
                                         marketIdInt)
                    events.putContract(marketIdInt, smkContract)
        return events

class AccountState(object):
    def __init__(self, accountStateMessage):
        self.id=uuid_to_integer(accountStateMessage.account_state.account)
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
        self.id=uuid_to_integer(orderAcceptedMessage.order_accepted.order)
    def __str__(self):
        return ("Bet(id=%s)"%(self.id))
    def __repr__(self):
        return self.__str__()

class SmkBroker():
    LOGGER = logging.getLogger('[smk.broker]')

    def __init__(self, client):
        self.client = client
        self.smkResponsePayload = None

    def dataHandlingCallback(self, message):
        self.smkResponsePayload = message
        self.LOGGER.debug("smk data received")
        
    def getSmkResponse(self, clientAction, expectedResponseType):
        callback = lambda message: self.dataHandlingCallback(message)
        self.client.add_handler(expectedResponseType, callback)
        clientAction()
        self.client.flush()
        self.client.read()
        self.client.del_handler(expectedResponseType, callback)
        self.LOGGER.debug("smk data transfered for %s"%expectedResponseType)
        return self.smkResponsePayload
        
    #unused
    def getAccountState(self):
        return AccountState(self.getSmkResponse(lambda: self.client.request_account_state(), 'seto.account_state'))

    #unused, add processing of successful response payload  
    def getBetsForAccount(self):
        return self.getSmkResponse(lambda: self.client.request_orders_for_account(), 'seto.orders_for_account')

    #unused, add processing of successful and problematic response payload  
    def placeBet(self, marketId, contractId, quantity, price):
        order = smarkets.Order()
        order.quantity = quantity#pounds*10000
        order.price = price#procents*100
        order.side = smarkets.Order.BUY
        
        order.market = self.intToUuid128(marketId)
        order.contract = self.intToUuid128(contractId)
        
        return Bet(self.getSmkResponse(lambda: self.client.order(order), 'seto.order_accepted'))#add nonsuccessful case:seto.order_rejected

    def cancelBet(self, orderId):
        order = self.intToUuid128(orderId)
        return self.getSmkResponse(lambda: self.client.order_cancel(order), 'seto.order_cancelled')#add nonsuccessful case:seto.order_rejected
    
    def intToUuid128(self, sourceInt):
        sourceUuid = Uuid.from_int(sourceInt, 'Account')
        resultedUuid = seto.Uuid128()
        resultedUuid.low = sourceUuid.low
        resultedUuid.high = sourceUuid.high
        return resultedUuid
