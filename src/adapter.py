import logging
from ZSI.ServiceContainer import ServiceContainer, SOAPRequestHandler

from betfair.BFGlobalService_server import BFGlobalService

import adapter_context

LOGGER = logging.getLogger('[adapter]')

class WsdlSOAPRequestHandler(SOAPRequestHandler):

    def do_GET(self):
        wsdlfile = "./wsdl/BFGlobalService.wsdl"
        LOGGER.info("Responding with wsdl %s on http request" % wsdlfile)
        wsdl = open(wsdlfile).read()
        self.send_xml(wsdl)
        
def BetfairApiServer(port=80, services=(), RequestHandlerClass=SOAPRequestHandler):
    address = ('127.0.0.1', port)
    sc = ServiceContainer(address, RequestHandlerClass=RequestHandlerClass)
    for service in services:
        path = service.getPost()
        sc.setNode(service, path)
    sc.serve_forever()
    
LOGGER.info("Starting SMK_BETFAIR adapter on port %s" % adapter_context.BETFAIR_API_PORT)
BetfairApiServer(port=int(adapter_context.BETFAIR_API_PORT), services=[BFGlobalService()], RequestHandlerClass=WsdlSOAPRequestHandler)