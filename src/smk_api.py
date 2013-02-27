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
    
#unused, add cases to process successful and problematic response
def placeBet(client, marketId, contractId, quantity, price):
#    seto.order_rejected
    order = smarkets.Order()
    order.quantity = quantity#pounds*10000
    order.price = price#procents*100
    order.side = smarkets.Order.BUY
    order.market = client.str_to_uuid128(str(marketId))
    order.contract = client.str_to_uuid128(str(contractId))
    
    client.order(order)
    client.flush()
    client.read()
    
#unused, add cases to process successful response  
def getBetsForAccount(client):
#    seto.orders_for_account
    client.request_orders_for_account()
    client.flush()
    client.read()

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

class AccountStateBroker():
    LOGGER = logging.getLogger('[account.state.broker]')

    def __init__(self):
        self.accountStateMessage = None

    def httpDataFetchingCallback(self, message):
        self.LOGGER.debug("Received account state message: %s" % (text_format.MessageToString(message)))
        self.accountStateMessage = message
        
    def getAccountState(self, client):
        callback = lambda x: self.httpDataFetchingCallback(x)
        client.add_handler('seto.account_state', callback)
        client.request_account_state()
        client.flush()
        client.read()
        client.del_handler('seto.account_state', callback)
        return AccountState(self.accountStateMessage)
