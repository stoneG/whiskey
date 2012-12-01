from BaseHTTPServer import BaseHTTPRequestHandler # used for request parsing
import os
import pdb
from StringIO import StringIO
import socket
import sys
import time
from urlparse import urlparse


class Whiskey(object):
    def __init__(self, app):
        self.app = app
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def brew(self, socket, addr):
        """Make server method."""

        self.s.bind(addr)
        self.s.listen(3)

        env = dict(os.environ.items())
        env['wsgi.input'] = sys.stdin
        env['wsgi.errors'] = sys.stderr
        env['wsgi.version'] = (1, 0)
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = True
        env['wsgi.run_once'] = True
        env['wsgi.url_scheme'] = 'http'

        env['REQUEST_METHOD'] = 'GET' # See PEP 333 for definitions
        env['SCRIPT_NAME'] = '/projects'
        env['PATH_INFO'] = '/one.html'
        env['QUERY_STRING'] = 'view' # after ? if any
        env['CONTENT_TYPE'] = '' # ie JSON
        env['CONTENT_LENGTH'] = '' # int
        env['SERVER_NAME'] = 'localhost'
        env['SERVER_PORT'] = '13373'
        env['SERVER_PROTOCOL'] = 'HTTP/1.1'
        # HTTP_ too?

    def drink(self):
        """Run method."""
        while True:
            print '\nWaiting for connection'
            conn, addr = self.s.accept()
            pid = os.fork()
            if pid == 0:
                print 'Accepted connection from:', addr
                request = conn.recv(1024)
                request = msg.decode()
                parse = HTTPRequest(request)
                self.build_environ(parse)
                # parse HTTP request, close conn
                # build environ
                # pass to app
                os._exit(0)
            else:
                conn.close()
                continue

    def start_response(status, response_headers, exc_info=None):
        pass

class Bartender(object):
    """Handles whiskey requests."""

class HTTPRequest(BaseHTTPRequestHandler):
    """Parses HTTP Requests."""
    def __init__(self, request):
        self.rfile = StringIO(request)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

def distill(host, port, app, server=Whiskey, handler=Bartender):
    """Instantiate Whiskey on host and port, communicating with app."""
    whiskey = Whiskey((host, port), handler)
    whiskey.set_app(app)
    return server
