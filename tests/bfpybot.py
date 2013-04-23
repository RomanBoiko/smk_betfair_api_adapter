import sys
sys.path.append('dependencies/bfpy/src')

import bfpy.bfclient as bfpy
from bfpy.bferror import BfError

bf = bfpy.BfClient()

try:
    bfrespLogin = bf.login(username='username', password='password')
    print bfrespLogin
    bfrespEventTypes = bf.getAllEventTypes()
    print bfrespEventTypes
except BfError, e:
    print "login error: %s" % str(e)
else:
    print "Test succeeded"