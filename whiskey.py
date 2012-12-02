from BaseHTTPServer import BaseHTTPRequestHandler # used for request parsing
import os
import pdb
from StringIO import StringIO
import socket
import sys
import time
from urlparse import urlparse


class Whiskey(object):
    def __init__(self, addr):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.headers_set = []
        self.headers_sent = []
        self.addr = addr
        self.brew(self.s)

    def brew(self, socket):
        """Make server method."""

        self.s.bind(self.addr)
        self.s.listen(3)

        env = self.environ = dict(os.environ.items())
        env['wsgi.input'] = sys.stdin
        env['wsgi.errors'] = sys.stderr
        env['wsgi.version'] = (1, 0)
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = True
        env['wsgi.run_once'] = True
        env['wsgi.url_scheme'] = 'http'

    def drink_forever(self):
        """Run method."""
        while True:
            print '\nWaiting for connection'
            conn, addr = self.s.accept()
            pid = os.fork()
            if pid == 0:
                #pdb.set_trace()
                print 'Accepted connection from:', addr
                request = conn.recv(1024)
                request = request.decode()
                parse = HTTPRequest(request)
                bartender = Bartender()
                self.environ = bartender.build_environ(self.environ, parse)
                if self.environ == None:
                    conn.close()
                    os._exit(0)
                else:
                    result = self.app(self.environ, self.start_response)
                    try:
                        for data in result:
                            if data:    # don't send headers until body appears
                                self.respond(data)
                        if not headers_sent:
                            self.respond('')   # send headers now if body was empty
                    finally:
                        if hasattr(result, 'close'):
                            result.close()
                        conn.close()
                        os._exit(0)
            else:
                conn.close()
                continue

    #def start_response(status, response_headers, exc_info=None):
    #    if exc_info:
    #        try:
    #            if self.headers_sent:
    #                # Re-raise original exception if headers sent
    #                raise exc_info[0], exc_info[1], exc_info[2]
    #        finally:
    #            exc_info = None     # avoid dangling circular ref
    #    elif self.headers_set:
    #        raise AssertionError("Headers already set!")

    #    self.headers_set[:] = [status, response_headers]

    def start_response(self, status, response_headers, exc_info=None):
        pass

    #def respond(self, data):
    #    if not self.headers_set:
    #         raise AssertionError("write() before start_response()")

    #    elif not self.headers_sent:
    #         # Before the first output, send the stored headers
    #         status, response_headers = self.headers_sent[:] = self.headers_set
    #         print 'Status: %s\r\n' % status
    #         for header in response_headers:
    #             print '%s: %s\r\n' % header
    #         print '\r\n'

    def respond(self, data):
        print data

    def set_app(self, app):
        self.app = app


class Bartender(object):
    """Handles whiskey requests."""

    def build_environ(self, env, parse):
        if parse.error_code != None:
            # Panic
            print 'Parse Error Code: {0}\nMessage: {1}'.format(parse.error_code,
                                                               parse.error_message)
            return None
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
        if url.path == '':
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
    whiskey = Whiskey((host, port))
    whiskey.set_app(app)
    whiskey.drink_forever()
    return whiskey
