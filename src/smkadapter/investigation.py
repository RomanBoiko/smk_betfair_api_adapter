import logging
import traceback
import sys
from google.protobuf import text_format

import smk_api
import adapter_context

LOG = logging.getLogger('[investigation]')

def global_callback(message_name, message):
    LOG.error("[global] Received a %s: %s" % 
                 (message_name,
                  text_format.MessageToString(message)))

def smkAction(action):
    client=smk_api.login(adapter_context.TEST_SMK_LOGIN, adapter_context.TEST_SMK_PASSWORD).result
    client.client.add_global_handler(global_callback)

    try:
        LOG.info("[action result] %s"%str(action(client).result))
    except:
        LOG.error("**********error occured")
        LOG.error("Unexpected error: %s", traceback.format_exc())
        
    finally:
        client.logout()

def main():
    if len(sys.argv) < 2:
        LOG.error("==>command line argument not specified")
    else:
        option = sys.argv[1]
        if option == "events":
            smkAction(lambda client: client.footballActiveEvents())
        elif option == "bet":
            quantity = 22
            price = 240
            isBuyer = True
            smkAction(lambda client: client.placeBet(369133, 573521, quantity, price, isBuyer))
        elif option == "cancel":
            smkAction(lambda client: client.cancelBet(84181761152778484))
            smkAction(lambda client: client.cancelBet(84181754822673358))
            smkAction(lambda client: client.cancelBet(84181744266264497))
        elif option == "account":
            smkAction(lambda client: client.getAccountState())
        elif option == "bets":
            smkAction(lambda client: client.getBetsForAccount())
        elif option == "prices":
            smkAction(lambda client: client.getMarketPrices(369133))
        else:
            print "==>invalid command line argument: %s" % option

if __name__ == "__main__":
    main()