import time
import threading

def myfunc(client):
    for i in range(10):
        print "sleeping 1 sec (client=%s) from thread %d" % (client, i)
        time.sleep(1)
        print "finished sleeping from thread %d" % i

t = threading.Thread(target=myfunc, args=("CCC",))
t.daemon = True
t.start()

time.sleep(8)