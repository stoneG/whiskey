import os
import pdb
import random
import sys
import time

def application(environ, start_response):
    if '.ico' in environ['PATH_INFO']:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['']
    def response():
        a = 0
        while a < 5:
            yield 'counting...\n'
            yield '{0}\n'.format(str(a))
            try:
                maybe_error(a)
            except:
                start_response('500 Internal Server Error', response_headers, sys.exc_info())
            a += 1
            time.sleep(1)
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    #wsgi_environ = [(key, val) for (key, val) in environ.items() if key not in os.environ]
    #for pair in wsgi_environ:
    #    print pair
    return response()

def maybe_error(a):
    random.seed(time.time())
    if random.random() < 0.45 and a > 0:
        return 1/0
