import logging
import smarkets
import adapter_context

logging.basicConfig(level=logging.DEBUG)

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


#market_id = client.str_to_uuid128('fc024')
#client.subscribe(market_id) # subscribe to a market
#client.flush()
#client.read()

# order = smarkets.Order()
# order.quantity = 400000 # 40 pounds payout
# order.price = 2500 # 25.00%
# order.side = smarkets.Order.BUY
# order.market = market_id
# order.contract = client.str_to_uuid128('fcccc')
# client.order(order)
# client.flush()
# client.read()
