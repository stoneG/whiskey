import os
import sys

class Whiskey(object):
    def __init__(self, app):
        self.app = app

    def brew(self, socket, addr):
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
        pass

    def start_response(status, response_headers, exc_info=None):
        pass
