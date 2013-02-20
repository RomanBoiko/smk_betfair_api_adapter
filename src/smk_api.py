import smarkets
import adapter_context
from google.protobuf import text_format
import smarkets.seto.piqi_pb2 as seto
import logging

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

class SmkDate(object):
    def __init__(self, year=2013, month=2, day=20):
        self.year=year
        self.month=month
        self.day=day

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
