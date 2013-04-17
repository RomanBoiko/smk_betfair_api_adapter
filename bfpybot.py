import bfpy.bfclient as bfpy
from bfpy.bferror import BfError

bf = bfpy.BfClient()

try:
    bfresp = bf.login(username='username', password='password')
except BfError, e:
    print "login error: %s" % str(e)
else:
    print bfresp
