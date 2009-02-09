#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008-2009 Wilson Pinto Júnior <wilson@openlanhouse.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import mimetypes
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from views import URLS

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        found = False
        for url in URLS:
            match = re.match(url[0], self.path)
            if match:
                url[1](self, *match.groups())
                found = True
                break
        
        if not found:
            self.send_error(404, 'Method not found')
    
    def send_file(self, fullpath):
        mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
        
        f = open(fullpath)
        self.send_response(200)
        self.send_header('Content-type',	mimetype)
        self.end_headers()
        self.wfile.write(f.read())
        
        f.close()

def main():
    try:
        server = HTTPServer(('', 8002), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
