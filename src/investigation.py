import logging
import sys
from google.protobuf import text_format

import smarkets
import smarkets.seto.piqi_pb2 as seto

import smk_api
from smk_api import EventsBroker,SmkDate
import adapter_context

LOGGER = logging.getLogger('[investigation]')

def global_callback(message_name, message):
    LOGGER.error("------------------> [global] Received a %s: %s" % 
                 (message_name,
                  text_format.MessageToString(message)))
def logger_callback(message):
    LOGGER.error("################### Received: %s" % (text_format.MessageToString(message)))


def doWithClient(client, eventRequest):
    LOGGER.info("=============>%s events request"%eventRequest)
    client.request_events(eventRequest)
    client.flush()
    client.read()

def doWithHttpService(serviceUrl):
    LOGGER.info("=============>%s response"%serviceUrl)
    content_type, result = smarkets.urls.fetch(serviceUrl)
    if content_type == 'application/x-protobuf':
        incoming_payload = seto.Events()
        incoming_payload.ParseFromString(result)
        print "===>%s" % text_format.MessageToString(incoming_payload)

def accountState(client):
    client.add_handler('seto.account_state', logger_callback)
    client.request_account_state()
    client.flush()
    client.read()


client = smk_api.login(adapter_context.TEST_SMK_LOGIN, adapter_context.TEST_SMK_PASSWORD)
#client.add_global_handler(global_callback)

try:
#    smarkets.events.Politics())
#    smarkets.events.CurrentAffairs())
    eventsBroker = EventsBroker()
    eventsMessage = eventsBroker.getEvents(client, smarkets.events.FootballByDate(SmkDate()))
#    LOGGER.warn("==>"+str(eventsMessage.with_markets[0]))
    for parent in eventsMessage.parents:
#        LOGGER.warn("==>GRAND_PARENT: "+str(parent))
        LOGGER.warn("==>GRAND_PARENT: id=%s, name=%s"%(str(parent.event.low), parent.name))
    for event in eventsMessage.with_markets:
        LOGGER.warn("==>EVENT_PARENT: id=%s, name=%s"%(str(event.event.low), event.name))
        for markets in event.markets:
            str(1)
#            LOGGER.warn("==> id=%s, name=%s"%(str(markets.market.low), markets.name))
#    parents(smarkets.seto.piqi_pb2.EventInfo), with_markets(smarkets.seto.piqi_pb2.EventInfo)
#    
#    accountState(client)
except:
    LOGGER.error("**********error occured")
    LOGGER.error("Unexpected error: %s", sys.exc_info())
finally:
    smk_api.logout(client)
