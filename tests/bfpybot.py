import sys
sys.path.append('dependencies/bfpy/src')

import bfpy.bfclient as bfpy
from bfpy.bferror import BfError

bf = bfpy.BfClient()

try:
    bfresp = bf.login(username='login', password='pass')
except BfError, e:
    print "login error: %s" % str(e)
else:
    print bfresp
