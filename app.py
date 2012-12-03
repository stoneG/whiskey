import pdb

def application(environ, start_response):
    env_list = []
    for key, value in environ.items():
        if type(value) != str:
            environ[key] = str(value)
    env_list = [': '.join(pair) for pair in environ.items()]
    script_name = '{0}: {1}\r\n'.format('SCRIPT_NAME', environ['SCRIPT_NAME'])
    path_info = '{0}: {1}\r\n'.format('PATH_INFO', environ['PATH_INFO'])
    query_string = '{0}: {1}\r\n'.format('QUERY_STRING', environ['QUERY_STRING'])
    response_body = script_name + path_info + query_string + '\r\n'.join(env_list)
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain'),
                        ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)
    return [response_body]
