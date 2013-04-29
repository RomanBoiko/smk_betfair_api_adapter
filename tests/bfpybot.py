import sys
import unittest
sys.path.append('dependencies/bfpy/src')

import bfpy
import bfpy.bfclient as bfclient
from bfpy.bferror import BfError

import smkadapter.adapter_context as adapter_context

def run_business_flow():
    bf = bfclient.BfClient()

    try:
        bfrespLogin = bf.login(username=adapter_context.TEST_SMK_LOGIN, password=adapter_context.TEST_SMK_PASSWORD)
        print bfrespLogin

        # accountFundsResponse = bf.getAccountFunds(bfpy.ExchangeUK)
        # print accountFundsResponse

        # bfrespEventTypes = bf.getAllEventTypes()
        # print bfrespEventTypes

        # currentBets = bf.getCurrentBets(bfpy.ExchangeUK)
        # print currentBets
        
        # self.placeBets(bf)

        bfLogout = bf.logout()
        print bfLogout
    except BfError, e:
        print "adapter error: %s" % str(e)
        raise

def placeBets(bf):
    placeBet = bf.createPlaceBets()

    placeBet.asianLineId = 0
    # Man City = 47999
    # Chelsea = 55190
    placeBet.selectionId = 200153
    placeBet.price = 500.0
    placeBet.size = 2.0
    placeBet.bspLiability = 0.0
    placeBet.betType = 'B'
    placeBet.betCategoryType = 'E'
    placeBet.betPersistenceType = 'NONE'
    # English Premier League Winner 2011/2012
    placeBet.marketId = 135615
    
    response = bf.placeBets(bfpy.ExchangeUK, bets=[placeBet])
    print response
#        print 'sleeping 5 seconds'
#        bet = response.betResults[0]

class AdapterExternalAcceptanceTest(unittest.TestCase):
    def test_adapter_flow(self):
        run_business_flow()

