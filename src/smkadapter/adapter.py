import logging
import threading
import BaseHTTPServer
import SimpleHTTPServer

import adapter_context
import betfair_api_nozsi

LOGGER = logging.getLogger('[adapter]')

class NoZsiPostHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        request_string = self.rfile.read(length)
        print "====>"+request_string
        result = betfair_api_nozsi.dispatchRequest(request_string)
        self.wfile.write(result)


def betfairApiServer():
    """Start the server."""
    noZsiPort = adapter_context.BETFAIR_API_PORT
    server_address = ("127.0.0.1", noZsiPort)
    server = BaseHTTPServer.HTTPServer(server_address, NoZsiPostHandler)
    LOGGER.info("Starting SMK_BETFAIR adapter on port %s (noZsi)" % str(noZsiPort))
    server.serve_forever()

def startThread(targetService):
    serviceThread = threading.Thread(target=targetService)
    serviceThread.daemon = True
    serviceThread.start()
    return serviceThread

if __name__ == "__main__":
    betfairApiServer()
