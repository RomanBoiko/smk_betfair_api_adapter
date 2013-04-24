import logging
import threading
import BaseHTTPServer
import SimpleHTTPServer

from ZSI.ServiceContainer import ServiceContainer, SOAPRequestHandler

from betfair.BFGlobalService_server import BFGlobalService
from betfair.BFExchangeService_server import BFExchangeService


import adapter_context
import betfair_api_nozsi

LOGGER = logging.getLogger('[adapter]')

class WsdlSOAPRequestHandler(SOAPRequestHandler):

    def do_GET(self):
        wsdlfile = "./wsdl/BFGlobalService.wsdl"
        if self.requestline.count("exchange") > 0:
            wsdlfile = "./wsdl/BFExchangeService.wsdl"
        LOGGER.info("Responding with wsdl ( %s ) on http GET request( %s )" % (wsdlfile, self.requestline))
        wsdl = open(wsdlfile).read()
        self.send_xml(wsdl)

def start_zsi_server(port=80, services=(), RequestHandlerClass=SOAPRequestHandler):
    address = ('127.0.0.1', port)
    sc = ServiceContainer(address, RequestHandlerClass=RequestHandlerClass)
    for service in services:
        path = service.getPost()
        sc.setNode(service, path)
    LOGGER.info("Starting SMK_BETFAIR adapter on port %s" % adapter_context.BETFAIR_API_PORT)
    sc.serve_forever()



class NoZsiPostHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        request_string = self.rfile.read(length)
        print "====>"+request_string
        result = betfair_api_nozsi.dispatchRequest(request_string)
        self.wfile.write(result)


def start_no_zsi_server():
    """Start the server."""
    noZsiPort = 8889
    server_address = ("127.0.0.1", noZsiPort)
    server = BaseHTTPServer.HTTPServer(server_address, NoZsiPostHandler)
    LOGGER.info("Starting SMK_BETFAIR adapter on port %s (noZsi)" % str(noZsiPort))
    server.serve_forever()

if __name__ == "__main__":
    noZsiThread = threading.Thread(target=start_no_zsi_server)
    noZsiThread.daemon = True
    noZsiThread.start()
    start_zsi_server(port=int(adapter_context.BETFAIR_API_PORT), services=[BFGlobalService(), BFExchangeService()], RequestHandlerClass=WsdlSOAPRequestHandler)
