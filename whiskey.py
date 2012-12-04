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
        self.headers_set = []
        self.headers_sent = []
        self.addr = addr
        self.make_server()

    def make_server(self):
        """Instantiates socket to self.s."""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def drink_forever(self):
        """Run method."""

        self.s.bind(self.addr)
        self.s.listen(3)

        while True:
            print '\nWaiting for connection'
            conn, addr = self.s.accept()
            pid = os.fork()
            if pid == 0: # if in child process
                print 'Accepted connection from:', addr
                request = conn.recv(1024)
                request = request.decode()
                try:
                    self.build_environ(request)
                except ParseError:
                    self.whiskey_response('400 Bad Request', conn)
                    conn.close()
                    os._exit(0)
                else:
                    result = self.app(self.environ, self.start_response)
                    try:
                        for element in result:
                            if element: # don't send headers until elements appear
                                self.app_response(element, conn)
                        if not self.headers_sent:
                            self.app_response('', conn) # send headers now if body was empty
                    finally:
                        if hasattr(result, 'close'):
                            result.close() # in case result is a file object
                        print 'Closing connection'
                        conn.close()
                        os._exit(0)
            else:
                conn.close()

    def start_response(self, status, response_headers, exc_info=None):
        """Sets response headers to self.headers_set."""
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
        self._additional_headers()

    def additional_headers(self):
        """Adds additional headers that the app omits."""
        # TODO: figure out what needs to go here
        # Date:
        # Server:
        pass


    def app_response(self, element, conn, status=None):
        """Sends app response to client."""
        response = element
        if not self.headers_set:
             raise AssertionError("Trying to respond() before start_response()")

        elif not self.headers_sent:
             # Before the first output, send the stored headers
             status, headers = self.headers_sent = self.headers_set
             rn = '\r\n'
             headers = [': '.join(header) for header in headers]
             response = 'HTTP/1.1' + status + rn + rn.join(headers) + rn*2 + element

        response = response.encode('utf-8')
        print 'Serving request'
        conn.send(response)

    def server_response(self, status, conn):
        """Sends server response to client."""
        if status:
            status = status.encode('utf-8')
            conn.send(status)

    def set_app(self, app):
        self.app = app

    def build_environ(self, request):
        """Given the request unicode str, build self.environ."""
        request = Parse(request)

        if request.error_code is not None:
            err = 'Parse Error Code: {0}\nMessage: {1}'.format(request.error_code,
                                                               request.error_message)
            print 'Sent error code to client'
            raise ParseError(err)

        # See PEP 333 for definitions
        # WSGI specific environ variables
        env = self.environ = dict(os.environ.items())
        env['wsgi.input'] = sys.stdin # TODO: Understand this
        env['wsgi.errors'] = sys.stderr # TODO: Understand this
        env['wsgi.version'] = (1, 0)
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = True
        env['wsgi.run_once'] = True
        env['wsgi.url_scheme'] = 'http'

        # Environ variables shared with CGI
        h = request.headers
        env['REQUEST_METHOD'] = request.command
        env['CONTENT_TYPE'] = h.type
        env['CONTENT_LENGTH'] = h['content-length'] if 'content-length' in h else ''
        env['SERVER_NAME'] = h['host'].split(':')[0] if 'host' in h else ''
        env['SERVER_PORT'] = h['host'].split(':')[1] if 'host' in h else ''
        env['SERVER_PROTOCOL'] = request.request_version
        # NOTE: Maybe add optional environ variables ie: REMOTE_HOST, REMOTE_ADDR

        for header in h.headers:
            # h.headers = ['environ-var:value', etc...]
            key, val = header.split(':', 1)
            key = key.replace('-', '_').upper()
            val = val.strip()
            if key in env:
                continue
            if 'HTTP_'+key in env:
                env['HTTP_'+key] += ',' + val
            else:
                env['HTTP_'+key] = val

        url = urlparse(request.path)
        if url.path == '':
            url.path = '/'
        env['SCRIPT_NAME'] = ''
        env['PATH_INFO'] = url.path
        env['QUERY_STRING'] = url.query

class Parse(BaseHTTPRequestHandler):
    """Parses HTTP Requests."""
    def __init__(self, request):
        self.rfile = StringIO(request)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def distill(host, port, app):
    """Instantiate Whiskey on host and port, communicating with app."""
    whiskey = Whiskey((host, port))
    whiskey.set_app(app)
    return whiskey
