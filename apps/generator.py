import os
import pdb
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
            a += 1
            time.sleep(1)
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    wsgi_environ = [(key, val) for (key, val) in environ.items() if key not in os.environ]
    for pair in wsgi_environ:
        print pair
    return response()
