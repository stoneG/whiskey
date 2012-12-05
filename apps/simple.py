import os
import pdb
import time

def application(environ, start_response):
    if '.ico' in environ['PATH_INFO']:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['']
    env_list = []
    for key, value in environ.items():
        if type(value) != str:
            environ[key] = str(value)
    wsgi_environ = [(key, val) for (key, val) in environ.items() if key not in os.environ]
    env_list = [': '.join(pair) for pair in wsgi_environ]
    script_name = '{0}: {1}\r\n'.format('SCRIPT_NAME', environ['SCRIPT_NAME'])
    path_info = '{0}: {1}\r\n'.format('PATH_INFO', environ['PATH_INFO'])
    query_string = '{0}: {1}\r\n'.format('QUERY_STRING', environ['QUERY_STRING'])
    response_body = script_name + path_info + query_string + '\r\n'.join(env_list)
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain'),
                        ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)
    return [response_body]
