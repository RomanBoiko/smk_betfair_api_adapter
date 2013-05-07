from __future__ import unicode_literals

import logging
import threading
import BaseHTTPServer
import SimpleHTTPServer

import adapter_context
import betfair_api

LOG = logging.getLogger('[adapter]')

class NoZsiPostHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        adapterRequest = self.rfile.read(length)
        LOG.debug("adapter_request: [%s]"%adapterRequest)
        adapterResponse = betfair_api.dispatchRequest(adapterRequest)
        LOG.debug("adapter_response: [%s]"%adapterResponse)
        self.wfile.write(adapterResponse.encode('utf-8'))


def betfairApiServer():
    """Start the server."""
    noZsiPort = int(adapter_context.BETFAIR_API_PORT)
    server_address = ("127.0.0.1", noZsiPort)
    server = BaseHTTPServer.HTTPServer(server_address, NoZsiPostHandler)
    LOG.info("==========================================")
    LOG.info("Starting SMK_BETFAIR_ADAPTER on port %s" % str(noZsiPort))
    LOG.info("==========================================")
    server.serve_forever()

def startThread(targetService):
    serviceThread = threading.Thread(target=targetService)
    serviceThread.daemon = True
    serviceThread.start()
    return serviceThread

if __name__ == "__main__":
    betfairApiServer()
