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
        self.headers_set = []
        self.headers_sent = []

    def brew(self, socket, addr):
        """Make server method."""

        self.s.bind(addr)
        self.s.listen(3)

        env = self.environ = dict(os.environ.items())
        env['wsgi.input'] = sys.stdin
        env['wsgi.errors'] = sys.stderr
        env['wsgi.version'] = (1, 0)
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = True
        env['wsgi.run_once'] = True
        env['wsgi.url_scheme'] = 'http'

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
                bartender = Bartender()
                self.environ = bartender.build_environ(parse)
                if self.environ == None:
                    conn.close()
                    os._exit(0)
                else:
                    # pass to app
                    os._exit(0)
            else:
                conn.close()
                continue

    def start_response(status, response_headers, exc_info=None):
        if exc_info:
            try:
                if self.headers_sent:
                    # Re-raise original exception if headers sent
                    raise exc_info[0], exc_info[1], exc_info[2]
            finally:
                exc_info = None     # avoid dangling circular ref
        elif self.headers_set:
            raise AssertionError("Headers already set!")

        self.headers_set = [status, response_headers]

def add_to_environ(key, env, parse):
    env[key] = parse.headers

    def start_response(status, response_headers, exc_info=None):
        pass

class Bartender(object):
    """Handles whiskey requests."""

    def build_environ(self, parse):
        if parse.error_code != None:
            # Panic
            print 'Parse Error Code: {0}\nMessage: {1}'.format(parse.error_code,
                                                               parse.error_message)
            return None
        env = self.environ
        # See PEP 333 for definitions
        h = parse.headers
        env['REQUEST_METHOD'] = parse.command
        env['CONTENT_TYPE'] = h.type
        env['CONTENT_LENGTH'] = h['content-length'] if 'content-length' in h else ''
        env['SERVER_NAME'] = h['host'].split(':')[0] if 'host' in h else ''
        env['SERVER_PORT'] = h['host'].split(':')[1] if 'host' in h else ''
        env['SERVER_PROTOCOL'] = parse.request_version
        # REMOTE_HOST
        # REMOTE_ADDR

        for header in parse.headers.headers:
            key, val = header.split(':', 1)
            key = key.replace('-', '_').upper()
            val = val.strip()
            if key in env:
                continue
            if 'HTTP_'+key in env:
                env['HTTP_'+key] += ',' + val
            else:
                env['HTTP_'+key] = val

        url = urlparse(parse.path)
        if url.path == ''
            url.path = '/'
        path_split = url.path.split('/')
        env['SCRIPT_NAME'] = '/'.join(path_split[:-1])
        path_info = path_split[-1] if path_split[-1] != '' else ''
        env['PATH_INFO'] = path_info
        env['QUERY_STRING'] = url.query
        return env

    def handle(self):
        parse.raw_requestline = parse.rfile.readline()
        if not self.parse_request():
            return

        # get app


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
