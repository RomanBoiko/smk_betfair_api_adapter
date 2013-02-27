import logging
import sys
from google.protobuf import text_format

import smarkets
import smarkets.seto.piqi_pb2 as seto

import smk_api
from smk_api import EventsBroker
import adapter_context
import datetime

LOGGER = logging.getLogger('[investigation]')

def global_callback(message_name, message):
    LOGGER.error("------------------> [global] Received a %s: %s" % 
                 (message_name,
                  text_format.MessageToString(message)))
def logger_callback(message):
    LOGGER.error("################### Received: %s" % (text_format.MessageToString(message)))


client = smk_api.login(adapter_context.TEST_SMK_LOGIN, adapter_context.TEST_SMK_PASSWORD)
client.add_global_handler(global_callback)

try:
#    eventsBroker = EventsBroker()
#    eventsMessage = eventsBroker.getEvents(client, smarkets.events.FootballByDate(datetime.date(2013, 2, 28)))
#    eventsMessage = eventsBroker.getEvents(client, smarkets.events.HorseRacingByDate(datetime.date(2013, 2, 28)))
#    eventsMessage = eventsBroker.getEvents(client, smarkets.events.TennisByDate(datetime.date(2013, 2, 21)))
#    eventsMessage = eventsBroker.getEvents(client, smarkets.events.Politics())
#    eventsMessage = eventsBroker.getEvents(client, smarkets.events.SportOther())

    print "==============================>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
#    print "===> Data=%s"%smk_api.AccountStateBroker(client).getAccountState().cash
#    print "===> Data=%s"%smk_api.BetsForAccountBroker(client).getBetsForAccount()
    print "===> Data=%s"%smk_api.BetsPlacingBroker(client).placeBet(24402, 50724, 20000, 2500)



except:
    LOGGER.error("**********error occured")
    LOGGER.error("Unexpected error: %s", sys.exc_info())
finally:
    smk_api.logout(client)

    
#markets {
#  market {
#    low: 24402
#  }
#  contracts {
#    contract {
#      low: 50724
#    }
#    type: CONTRACT_GENERIC
#    slug: "asian_handicap_away_plus_3_25"
#    name: "Correcaminos de la UAT +3.25"
#  }
#  slug: "asian_handicap_away_plus_3_25"
#  name: "Asian handicap Correcaminos de la UAT +3.25"
#  shortname: "ATL vs. COR"
#}
#
#
#market {
#  low: 24367
#}
#contracts {
#  contract {
#    low: 50684
#  }
#  type: CONTRACT_OVER_UNDER
#  slug: "over"
#  name: "Over 5.5 goals"
#  shortname: "Over 5.5"
#}
#contracts {
#  contract {
#    low: 50683
#  }
#  type: CONTRACT_OVER_UNDER
#  slug: "under"
#  name: "Under 5.5 goals"
#  shortname: "Under 5.5"
#}
#slug: "over_under_5_5"
#name: "Over/under 5.5 for Atlante vs. Correcaminos UAT"
#shortname: "ATL vs. COR"
