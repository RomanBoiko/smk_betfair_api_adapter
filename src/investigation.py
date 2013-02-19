import smk_api
import adapter_context
import smarkets
from google.protobuf import text_format
import logging
import smarkets.seto.piqi_pb2 as seto
import sys

LOGGER = logging.getLogger('[investigation]')

def global_callback(message_name, message):
    LOGGER.error("------------------> [global] Received a %s: %s" % (message_name, text_format.MessageToString(message)))
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

#replace from http://vagrant-dev.corp.smarkets.com:37089/api/events/current-affairs/1.pb
doWithHttpService("http://api-sandbox.smarkets.com:37089/api/events/politics/1.pb")
doWithHttpService("http://api-sandbox.smarkets.com:37089/api/events/current-affairs/1.pb")

client = smk_api.login(adapter_context.TEST_SMK_LOGIN, adapter_context.TEST_SMK_PASSWORD)
client.add_global_handler(global_callback)

try:
    doWithClient(client, smarkets.events.Politics())
    doWithClient(client, smarkets.events.CurrentAffairs())
    accountState(client)
except:
    LOGGER.error("**********error occured")
    LOGGER.error("Unexpected error: %s", sys.exc_info())
finally:
    smk_api.logout(client)
