#!/usr/bin/env python
"""
A very simple HTTP server.
"""
import sys
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8080

address = ('localhost', port)
httpd = HTTPServer(address, SimpleHTTPRequestHandler)
sa = httpd.socket.getsockname()
print 'Now visit http://%s:%d' % sa
print 'Press CTRL-C to stop this server'
httpd.serve_forever()
