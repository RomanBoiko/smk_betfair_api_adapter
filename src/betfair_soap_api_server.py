from ZSI.ServiceContainer import ServiceContainer, SOAPRequestHandler
from betfair.BFGlobalService_server import *
import adapter_context

class MySOAPRequestHandler(SOAPRequestHandler):

    def do_GET(self):
        wsdlfile = "./wsdl/BFGlobalService.wsdl"
        print ">>>>> using wsdl file", wsdlfile
        wsdl = open(wsdlfile).read()
        self.send_xml(wsdl)
        
def BetfairApiServer(port=80, services=(), RequestHandlerClass=SOAPRequestHandler):
    address = ('127.0.0.1', port)
    sc = ServiceContainer(address, RequestHandlerClass=RequestHandlerClass)
    for service in services:
        path = service.getPost()
        sc.setNode(service, path)
    sc.serve_forever()
    
BetfairApiServer(port=int(adapter_context.BETFAIR_API_PORT), services=[BFGlobalService()], RequestHandlerClass=MySOAPRequestHandler)