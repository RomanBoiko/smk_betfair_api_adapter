import logging
import datetime
import traceback
import sys
from google.protobuf import text_format

import smk_api
import adapter_context

LOGGER = logging.getLogger('[investigation]')

def global_callback(message_name, message):
    LOGGER.error("============> [global] Received a %s: %s" % 
                 (message_name,
                  text_format.MessageToString(message)))

def smkAction(action):
    client=smk_api.login(adapter_context.TEST_SMK_LOGIN, adapter_context.TEST_SMK_PASSWORD).result
    client.client.add_global_handler(global_callback)

    try:
        print "===========>"+str(action(client))
    except:
        LOGGER.error("**********error occured")
        LOGGER.error("Unexpected error: %s", traceback.format_exc())
        
    finally:
        client.logout()

def main():
    if len(sys.argv) < 2:
        print "==>command line argument not specified"
    else:
        option = sys.argv[1]
        if option == "events":
            smkAction(lambda client: client.footballByDate(datetime.date(2013, 3, 5)))
        elif option == "bet":
            quantity = 22
            price = 2400
            smkAction(lambda client: client.placeBet(276267, 380942, quantity, price))
        elif option == "cancel":
            smkAction(lambda client: client.cancelBet(int(sys.argv[2])))
        elif option == "account":
            smkAction(lambda client: client.getAccountState())
        elif option == "bets":
            smkAction(lambda client: client.getBetsForAccount())
        else:
            print "==>invalid command line argument: %s" % option

if __name__ == "__main__":
    main()