import logging
import datetime
import traceback
from google.protobuf import text_format

import smk_api
import adapter_context
import smarkets

LOGGER = logging.getLogger('[investigation]')

def global_callback(message_name, message):
    LOGGER.error("------------------> [global] Received a %s: %s" % 
                 (message_name,
                  text_format.MessageToString(message)))
def logger_callback(message):
    LOGGER.error("################### Received: %s" % (text_format.MessageToString(message)))


client=smk_api.login(adapter_context.TEST_SMK_LOGIN, adapter_context.TEST_SMK_PASSWORD)
client.add_global_handler(global_callback)

QUANTITY = 220000
PRICE = 2400

try:
    smk_api.EventsBroker().getEvents(client, smarkets.events.FootballByDate(datetime.date(2013, 3, 1)))
    smk_api.SmkBroker(client).placeBet(24402, 50724, QUANTITY, PRICE)
    smk_api.SmkBroker(client).placeBet(276267, 380942, QUANTITY, PRICE)
    #            seto.order_accepted: type: PAYLOAD_ORDER_ACCEPTED
#        eto_payload {
#          seq: 3
#          is_replay: false
#        }
#        order_accepted {
#          seq: 3
#          order {
#            low: 81604562358242756
#          }
#        }

    smk_api.SmkBroker(client).cancelBet(81604558529447299)
            #    a seto.order_cancelled: type: PAYLOAD_ORDER_CANCELLED
        #        eto_payload {
        #          seq: 3
        #          is_replay: false
        #        }
        #        order_cancelled {
        #          order {
        #            low: 81604562358242756
        #          }
        #          reason: ORDER_CANCELLED_MEMBER_REQUESTED
        #        }
        
#        Received a seto.order_cancel_rejected: type: PAYLOAD_ORDER_CANCEL_REJECTED
#        eto_payload {
#          seq: 3
#          is_replay: false
#        }
#        order_cancel_rejected {
#          seq: 3
#          reason: ORDER_CANCEL_REJECTED_NOT_LIVE
#        }



    smk_api.SmkBroker(client).getAccountState()
            #seto.account_state: type: PAYLOAD_ACCOUNT_STATE
        #eto_payload {
        #  seq: 3
        #  is_replay: false
        #}
        #account_state {
        #  account {
        #    low: 13700964455177639
        #  }
        #  currency: CURRENCY_GBP
        #  cash {
        #    value: 100000
        #  }
        #  bonus {
        #    value: 0
        #  }
        #  exposure {
        #    value: -1056
        #  }
        #}


    smk_api.SmkBroker(client).getBetsForAccount()
    #                seto.orders_for_account: type: PAYLOAD_ORDERS_FOR_ACCOUNT
#            eto_payload {
#              seq: 3
#              is_replay: false
#            }
#            orders_for_account {
#              markets {
#                market {
#                  low: 276267
#                }
#                price_type: PRICE_PERCENT_ODDS
#                contracts {
#                  contract {
#                    low: 380942
#                  }
#                  bids {
#                    price: 2400
#                    orders {
#                      order {
#                        low: 81604562358242756
#                      }
#                      type: ORDER_CREATE_LIMIT
#                      status: ORDER_STATUS_LIVE
#                      quantity_type: QUANTITY_PAYOFF_CURRENCY
#                      quantity: 220000
#                      created_microseconds: 1362081552793358
#                    }
#                    orders {
#                      order {
#                        low: 81604558529447299
#                      }
#                      type: ORDER_CREATE_LIMIT
#                      status: ORDER_STATUS_LIVE
#                      quantity_type: QUANTITY_PAYOFF_CURRENCY
#                      quantity: 220000
#                      created_microseconds: 1362081470109609
#                    }
#                  }
#                }
#              }
#            }


except:
    LOGGER.error("**********error occured")
    LOGGER.error("Unexpected error: %s", traceback.format_exc())
    
finally:
    smk_api.logout(client)

