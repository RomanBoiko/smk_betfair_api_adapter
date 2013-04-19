import os
import urllib2

import BaseHTTPServer
import SimpleHTTPServer

from jinja2 import Template



PORT = 8888

def readFile(path):
    fileStream = urllib2.urlopen("file://%s"%os.path.abspath(path))
    data = fileStream.read()
    fileStream.close()
    return data

class PostHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        template = Template(readFile("templates/login.response.xml"))
        result_string = template.render(sessionid='session')
        
        length = int(self.headers.getheader('content-length'))
        request_string = self.rfile.read(length)
        print "====>"+request_string
        try:
            result = result_string
        except:
            result = 'error'
        self.wfile.write(result)


def start_server():
    """Start the server."""
    server_address = ("localhost", PORT)
    server = BaseHTTPServer.HTTPServer(server_address, PostHandler)
    server.serve_forever()

if __name__ == "__main__":
    start_server()