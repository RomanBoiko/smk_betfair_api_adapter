import logging

from google.protobuf import text_format

import smarkets
import smarkets.seto.piqi_pb2 as seto

import adapter_context

LOGGER = logging.getLogger('[smk.api]')

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

class EventsBroker():
    LOGGER = logging.getLogger('[events.broker]')

    def __init__(self):
        self.eventsMessage = None
        
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
        
    def getEvents(self, client, eventRequest):
        callback = lambda x: self.httpDataFetchingCallback(x)
        client.add_handler('seto.http_found', callback)
        client.request_events(eventRequest)
        client.flush()
        client.read()
        client.del_handler('seto.http_found', callback)
        return self.eventsMessage

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
