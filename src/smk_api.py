import logging

from google.protobuf import text_format

import smarkets
import smarkets.seto.piqi_pb2 as seto
from smarkets.uuid import Uuid, uuid_to_int

import adapter_context

LOGGER = logging.getLogger('[smk.api]')
FOOTBALL_EVENT_TYPE_ID = 121005

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
        self.parents = []
        self.parentToEvent={}
        self.eventToMarket={}

class Event(object):
    def __init__(self, eventId, eventName, eventTypeId):
        self.eventId = eventId
        self.eventName = eventName
        self.eventTypeId = eventTypeId

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
        for parent in eventsMessage.parents:
            eventDTO = Event(self.uuid_to_integer(parent.event), parent.name, FOOTBALL_EVENT_TYPE_ID)
            events.parents.append(eventDTO)
            events.parentToEvent[str(self.uuid_to_integer(parent.event))]=[]
        for sportEvent in eventsMessage.with_markets:
            eventDTO = Event(self.uuid_to_integer(sportEvent.event), sportEvent.name, FOOTBALL_EVENT_TYPE_ID)
            events.parentToEvent[str(self.uuid_to_integer(sportEvent.parent))].append(eventDTO)
            events.eventToMarket[str(self.uuid_to_integer(sportEvent.event))] = []
            for marketItem in sportEvent.markets :
                marketDTO = Market(self.uuid_to_integer(marketItem.market), marketItem.name, FOOTBALL_EVENT_TYPE_ID, self.uuid_to_integer(sportEvent.event))
                events.eventToMarket[str(self.uuid_to_integer(sportEvent.event))].append(marketDTO)
        return events
    
    def uuid_to_integer(self, uuid):
        uu = Uuid.from_int((uuid.high, uuid.low), 'Account')
        return uuid_to_int(uu.to_hex())

class AccountState(object):
    def __init__(self, accountStateMessage):
        self.id=accountStateMessage.account_state.account.low
        self.currency=accountStateMessage.account_state.currency
        self.cash=accountStateMessage.account_state.cash.value
        self.bonus=accountStateMessage.account_state.bonus.value#do we need that?
        self.exposure=accountStateMessage.account_state.exposure.value#do we need that?

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
        
        order.market = seto.Uuid128()
        order.market.low = marketId
        order.contract = seto.Uuid128()
        order.contract.low = contractId
        return self.getSmkResponse(lambda: self.client.order(order), 'seto.order_accepted')#add nonsuccessful case:seto.order_rejected

    def cancelBet(self, orderId):
        order = seto.Uuid128()
        order.low = orderId
        return self.getSmkResponse(lambda: self.client.order_cancel(order), 'seto.order_cancelled')#add nonsuccessful case:seto.order_rejected
