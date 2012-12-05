# The Content-Length supplied with this app will be too long

# GOOGLE CHROME will give the following error if the server doesn't
# fix Content-Length:
# Error 354 (net::ERR_CONTENT_LENGTH_MISMATCH): The server unexpectedly closed the connection.

# wsgiref.simple_server won't fix the content length. This server will
# just close the connection when the app is done.

import os
import pdb
import time

def application(environ, start_response):
    if '.ico' in environ['PATH_INFO']:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['']
    response_body = 'this is not 200 characters.'
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain'),
                        ('Content-Length', str(200))]
    start_response(status, response_headers)
    return [response_body]
