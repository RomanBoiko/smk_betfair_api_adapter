import logging
logging.basicConfig(level=logging.DEBUG)
import smarkets
username = 'username'
password = 'password'
settings = smarkets.SessionSettings(username, password)
settings.host = 'api-sandbox.smarkets.com'
settings.port = 3701

session = smarkets.Session(settings)
client = smarkets.Smarkets(session)
client.login()
client.ping()
client.flush()
client.read()

market_id = client.str_to_uuid128('fc024')
client.subscribe(market_id) # subscribe to a market
client.flush()
client.read()

# order = smarkets.Order()
# order.quantity = 400000 # 40 pounds payout
# order.price = 2500 # 25.00%
# order.side = smarkets.Order.BUY
# order.market = market_id
# order.contract = client.str_to_uuid128('fcccc')
# client.order(order)
# client.flush()
# client.read()

client.logout()
