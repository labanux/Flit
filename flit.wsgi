import sys
sys.path.insert(0, "/home/laban/public_html/flit")

from index import app as application

# Attempt to import 'socket' module.

#import socket

#def application(environ, start_response):
#    status = '200 OK'
#    output = 'Hello World!'
    
#    response_headers = [('Content-type', 'text/plain'),
#                            ('Content-Length', str(len(output)))]
#    start_response(status, response_headers)
    
#    return [output] 