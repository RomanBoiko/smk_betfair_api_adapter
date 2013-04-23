import sys
import unittest
sys.path.append('dependencies/bfpy/src')

import bfpy.bfclient as bfpy
from bfpy.bferror import BfError

import smkadapter.adapter_context as adapter_context

class AdapterExternalAcceptanceTest(unittest.TestCase):
    def test_adapter_flow(self):
        bf = bfpy.BfClient()

        try:
            bfrespLogin = bf.login(username=adapter_context.TEST_SMK_LOGIN, password=adapter_context.TEST_SMK_PASSWORD)
            print bfrespLogin
            bfrespEventTypes = bf.getAllEventTypes()
            print bfrespEventTypes
        except BfError, e:
            print "adapter error: %s" % str(e)
            raise
        else:
            print "Test succeeded"