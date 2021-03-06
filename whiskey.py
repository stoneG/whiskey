from BaseHTTPServer import BaseHTTPRequestHandler # used for request parsing
from datetime import datetime
import os
import pdb
from StringIO import StringIO
import socket
import sys
import time
import threading
from urlparse import urlparse


class Whiskey(object):
    """Whiskey is a WSGI compliant server. It supports the following
    environ variables:

                  TODO: FILL THESE OUT!
    CONTENT_LENGTH    :
    CONTENT_TYPE      :
    HTTP_             :
    PATH_INFO         :
    QUERY_STRING      :
    REQUEST_METHOD    :
    SCRIPT_NAME       :
    SERVER_NAME       :
    SERVER_PROTOCOL   :
    SERVER_PORT       :
    wsgi.errors       :
    wsgi.input        :
    wsgi.multiprocess :
    wsgi.multithread  :
    wsgi.run_once     :
    wsgi.url_scheme   :
    wsgi.version      :

    Additionally, all encoding/decoding is handled on the application
    side, so Whiskey should always be dealing with str or bytestrings.
    """


    def __init__(self, addr):
        self.headers_set = []
        self.headers_sent = []
        self.addr = addr
        self.response_content_length = None
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
                try:
                    self.build_environ(request)
                except ParseError:
                    self.whiskey_response('400 Bad Request', conn)
                    conn.close()
                    os._exit(0)
                else:
                    if self.environ['REQUEST_METHOD'].lower() == 'except':
                        self.server_response('100 Continue', conn)
                    result = self.app(self.environ, self.start_response)
                    self.add_server_headers(result)
                    self.determine_content_length(result)
                    try:
                        for element in result:
                            if element: # don't send headers until elements appear
                                self.app_response(element, conn)
                        if not self.headers_sent:
                            # send headers if body was empty
                            self.app_response('', conn)
                    except:
                        if not self.headers_sent:
                            self.server_response('500 Internal Server Error', conn)
                    finally:
                        if hasattr(result, 'close'):
                            result.close() # in case result is a file object
                        print 'Closing connection'
                        #for each in self.headers_sent:
                        #    print each
                        conn.close()
                        os._exit(0)
            else:
                conn.close()

    def start_response(self, status, response_headers, exc_info=None):
        """start_response is passed to the app, which sets response headers
        to self.headers_set.

        The app may call start_response multiple times, if and only if it
        provides exc_info.

        start_response must also return a response callable that legacy apps can
        use as a file-like stream. This makes it easy to convert old apps to be
        "WSGI compliant". Its use is deprecated because using a file-like stream
        puts the reins of execution in the hands of the app object, preventing
        intelligent content handling interleaving/asynchrony on the part of the
        server.
        """
        if exc_info:
            if self.headers_sent:
                # WSGI compliancy: this situation must raise this error
                # which should abort the app
                print 'app raised error:'
                print exc_info[0], exc_info[1], exc_info[2]
                raise exc_info[0], exc_info[1], exc_info[2]
        elif self.headers_set:
            raise AssertionError("Multiple calls to start_response,"+
                                 " headers already set!")

        self.headers_set = [status, response_headers]
        self.error_checking()
        return self.app_response

    def add_server_headers(self, response):
        """Adds additional headers that the app omits."""
        # TODO: figure out what needs to go here
        server_headers = ['Date', 'Server']
        if self.headers_set:
            headers_set_keys = [key for key, value in self.headers_set[1]]
            for header in server_headers:
                for index, key in enumerate(headers_set_keys):
                    if header == key:
                        del self.headers_set[1][index]
        for header in server_headers:
            self.headers_set[1] += [self.determine(header)]

    def determine(self, header):
        """Given a header key, return the tuple (header, value)."""
        if header == 'Date':
            return (header, self.date_time())
        elif header == 'Server':
            return (header, 'whiskey')

    def determine_content_length(self, response):
        """Given the response body, make sure the Content-Length header is
        valid. If no Content-Length header is provided by the app, try to
        produce it on the server-side.
        """
        try:
            length = len(response)
            response_body = ''.join(element for element in response)
            length = len(response_body)
        except TypeError:
            # The app returned a generator
            return
        if self.headers_set:
            headers_set_keys = [key for key, value in self.headers_set[1]]
            for index, key in enumerate(headers_set_keys):
                if 'Content-Length' == key:
                    self.response_content_length = int(self.headers_set[1][index][1])
            if self.response_content_length == None:
                self.response_content_length = length
        print 'cont-len is {0}'.format(self.response_content_length)

    def error_checking(self):
        # TODO: figure out what needs to go here
        pass

    def app_response(self, element, conn, status=None):
        """Sends app response to client."""
        if self.response_content_length != None:
            if self.response_content_length < len(element):
                element = element[:self.response_content_length]
            else:
                self.response_content_length - len(element)
        response = element
        if not self.headers_set:
             raise AssertionError("Trying to respond() before start_response()")
        elif not self.headers_sent:
             # Before the first output, send the stored headers
             status, headers = self.headers_sent = self.headers_set
             rn = '\r\n'
             headers = [': '.join(header) for header in headers]

             response = 'HTTP/1.1 ' + status + rn + rn.join(headers) + rn*2 + element

        print 'Serving app response'
        conn.send(response)

    def server_response(self, status, conn):
        """Sends server response to client."""
        if status:
            print 'Serving server response'
            response = 'HTTP/1.1 ' + status + '\r\n\r\n'
            conn.send(response)

    def set_app(self, app):
        self.app = app

    def build_environ(self, request):
        """Given the request str, build self.environ."""
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

        # Optional
        v = sys.version_info
        ss = 'Whiskey/0.1 Python/{0}.{1}.{2}'.format(v[0], v[1], v[2])
        env['SERVER_SOFTWARE'] = ss
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        #wsgi.file_wrapper: wsgiref.util.FileWrapper
        #REMOTE_ADDR: 127.0.0.1
        #REMOTE_HOST: localhost

    def date_time(self):
        """Return a string representation of a date according to RFC 1123
        (HTTP/1.1).
        """
        dt = datetime.now()
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][dt.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
            dt.year, dt.hour, dt.minute, dt.second)

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
