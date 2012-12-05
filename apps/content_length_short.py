# The Content-Length supplied with this app will be too short

# wsgiref.simple_server will fix the content length.
# so the client will only receive 'this is mo'

import os
import pdb
import time

def application(environ, start_response):
    if '.ico' in environ['PATH_INFO']:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['']
    response_body = 'this is more than 10 characters.'
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain'),
                        ('Content-Length', str(10))]
    start_response(status, response_headers)
    return [response_body]
