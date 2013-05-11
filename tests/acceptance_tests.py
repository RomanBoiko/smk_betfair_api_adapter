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

class BetfairAdapterAcceptanceTest(unittest.TestCase):

    def makePauseToAllowAdapterToStart(self):
        time.sleep(3)

    def test_real_flow_using_bfpy(self):
        self.makePauseToAllowAdapterToStart()
        bfClient = bfclient.BfClient()
        adapterResponse = bfClient.login(username=adapter_context.TEST_SMK_LOGIN, password=adapter_context.TEST_SMK_PASSWORD)
        LOG.debug(adapterResponse)
        try:
            adapterResponse = str(bfClient.keepAlive())
            LOG.debug(adapterResponse)

            adapterResponse = str(bfClient.getAccountFunds(bfpy.ExchangeUK))
            LOG.debug(adapterResponse)

            adapterResponse = str(bfClient.getAllEventTypes())
            LOG.debug(adapterResponse)

            adapterResponse = str(bfClient.getCurrentBets(bfpy.ExchangeUK))
            LOG.debug(adapterResponse)

            allMarkets = bfClient.getAllMarkets(bfpy.ExchangeUK)
            firstMarket = allMarkets.marketData[0]
            adapterResponse = str(allMarkets)
            LOG.debug(adapterResponse)

            adapterResponse = str(bfClient.getMarketPricesCompressed(bfpy.ExchangeUK, marketId=firstMarket.marketId))
            LOG.debug(adapterResponse)

            marketData = bfClient.getMarket(bfpy.ExchangeUK, marketId=firstMarket.marketId)
            adapterResponse = str(marketData)
            LOG.debug(adapterResponse)
            firstContract = marketData.market.runners[0]

            placeBet = bfClient.createPlaceBets()
            placeBet.asianLineId = 0
            placeBet.selectionId = firstContract.selectionId
            placeBet.price = 500
            placeBet.size = 2.0
            placeBet.bspLiability = 0.0
            placeBet.betType = 'B'
            placeBet.betCategoryType = 'E'
            placeBet.betPersistenceType = 'NONE'
            placeBet.marketId = firstMarket.marketId
            
            placeBetResponse = bfClient.placeBets(bfpy.ExchangeUK, bets=[placeBet])
            adapterResponse = str(placeBetResponse)
            LOG.debug(adapterResponse)

            bet = placeBetResponse.betResults[0]

            adapterResponse = str(bfClient.getBet(bfpy.ExchangeUK, betId=bet.betId))
            LOG.debug(adapterResponse)
            self.assertFalse("selectionName = \"Name for" in adapterResponse)
            self.assertFalse("marketName = \"Name for" in adapterResponse)

            cancelBet = bfClient.createCancelBets()
            cancelBet.betId = bet.betId

            adapterResponse = str(bfClient.cancelBets(bfpy.ExchangeUK, bets=[cancelBet]))
            LOG.debug(adapterResponse)

            adapterResponse = str(bfClient.cancelBetsByMarket(bfpy.ExchangeUK, markets=[firstMarket.marketId]))
            LOG.debug(adapterResponse)

            adapterResponse = str(bfClient.getMUBets(bfpy.ExchangeUK, marketId=276267, betStatus='M'))
            LOG.debug(adapterResponse)

        finally:
            adapterResponse = str(bfClient.logout())
            LOG.debug(adapterResponse)