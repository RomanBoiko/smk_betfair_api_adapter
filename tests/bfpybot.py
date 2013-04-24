import sys
import unittest
sys.path.append('dependencies/bfpy/src')

import bfpy
import bfpy.bfclient as bfclient
from bfpy.bferror import BfError

import smkadapter.adapter_context as adapter_context

class AdapterExternalAcceptanceTest(unittest.TestCase):
    def test_adapter_flow(self):
        bf = bfclient.BfClient()

        try:
            bfrespLogin = bf.login(username=adapter_context.TEST_SMK_LOGIN, password=adapter_context.TEST_SMK_PASSWORD)
            print bfrespLogin

            accountFundsResponse = bf.getAccountFunds(bfpy.ExchangeUK)
            print accountFundsResponse

            bfrespEventTypes = bf.getAllEventTypes()
            print bfrespEventTypes

            bfLogout = bf.logout()
            print bfLogout
        except BfError, e:
            print "adapter error: %s" % str(e)
            raise
        else:
            print "Test succeeded"
