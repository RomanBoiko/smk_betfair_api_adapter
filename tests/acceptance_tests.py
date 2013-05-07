import sys
import unittest
import time
import logging

sys.path.append('dependencies/bfpy/src')
import bfpy
import bfpy.bfclient as bfclient
from bfpy.bferror import BfError

from smkadapter import adapter_context

LOG = logging.getLogger('[adapter.test]')

TEST_MARKET_ID = 431881
TEST_CONTRACT_ID = id=703513

class BetfairAdapterAcceptanceTest(unittest.TestCase):

    def makePauseToAllowAdapterToStart(self):
        time.sleep(3)

    def test_real_flow_using_bfpy(self):
        self.makePauseToAllowAdapterToStart()
        bfClient = bfclient.BfClient()
        adapterResponse = bfClient.login(username=adapter_context.TEST_SMK_LOGIN, password=adapter_context.TEST_SMK_PASSWORD)
        LOG.debug(adapterResponse)
        try:
            adapterResponse = str(bfClient.getAccountFunds(bfpy.ExchangeUK))
            LOG.debug(adapterResponse)

            adapterResponse = str(bfClient.getAllEventTypes())
            LOG.debug(adapterResponse)

            adapterResponse = str(bfClient.getCurrentBets(bfpy.ExchangeUK))
            LOG.debug(adapterResponse)

            adapterResponse = str(bfClient.getMarketPricesCompressed(bfpy.ExchangeUK, marketId=TEST_MARKET_ID))
            LOG.debug(adapterResponse)

            placeBet = bfClient.createPlaceBets()
            placeBet.asianLineId = 0
            placeBet.selectionId = TEST_CONTRACT_ID
            placeBet.price = 500
            placeBet.size = 2.0
            placeBet.bspLiability = 0.0
            placeBet.betType = 'B'
            placeBet.betCategoryType = 'E'
            placeBet.betPersistenceType = 'NONE'
            placeBet.marketId = TEST_MARKET_ID
            
            placeBetResponse = bfClient.placeBets(bfpy.ExchangeUK, bets=[placeBet])
            adapterResponse = str(placeBetResponse)
            LOG.debug(adapterResponse)

            bet = placeBetResponse.betResults[0]

            cancelBet = bfClient.createCancelBets()
            cancelBet.betId = bet.betId

            adapterResponse = str(bfClient.cancelBets(bfpy.ExchangeUK, bets=[cancelBet]))
            LOG.debug(adapterResponse)
            
            adapterResponse = str(bfClient.cancelBetsByMarket(bfpy.ExchangeUK, markets=[TEST_MARKET_ID]))
            LOG.debug(adapterResponse)

            adapterResponse = str(bfClient.getAllMarkets(bfpy.ExchangeUK))
            LOG.debug(adapterResponse)

            
            adapterResponse = str(bfClient.getBet(bfpy.ExchangeUK, betId=84181754822673358))
            LOG.debug(adapterResponse)

            adapterResponse = str(bfClient.getMUBets(bfpy.ExchangeUK, marketId=276267, betStatus='M'))
            LOG.debug(adapterResponse)

        finally:
            adapterResponse = str(bfClient.logout())
            LOG.debug(adapterResponse)