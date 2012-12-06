import pdb
import socket
import sys

port = int(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def response():
    method = 'GET '
    url = '/ '
    http = 'HTTP/1.1'
    rn = '\r\n'
    resp = method + url + http + rn
    return resp

s.connect(('127.0.0.1', port))
s.send(response())
while True:
    data = s.recv(1024)
    if data == None or data == '':
        break
    else:
        print data
