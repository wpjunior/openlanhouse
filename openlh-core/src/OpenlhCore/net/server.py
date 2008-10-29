#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008 Wilson Pinto Júnior <wilson@openlanhouse.org>
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

import gobject
import socket
import logging
import traceback

try:
    from OpenlhCore.net.backends import gnutls_backend as gnutls
except Exception, error:
    print error
    gnutls = None

try:
    from OpenlhCore.net.backends import openssl_backend as openssl #this backend is not working now
except Exception, error:
    print error
    openssl = None

class NetServer(gobject.GObject):
    """
        Network Server Class
    """
    
    __gsignals__ = {'connected':(gobject.SIGNAL_RUN_FIRST,
                                     gobject.TYPE_NONE,
                                     (gobject.TYPE_PYOBJECT,
                                      gobject.TYPE_PYOBJECT,
                                      gobject.TYPE_PYOBJECT
                                     )),
                    
                    'disconnected':(gobject.SIGNAL_RUN_FIRST,
                                     gobject.TYPE_NONE,
                                     (gobject.TYPE_PYOBJECT,
                                      gobject.TYPE_PYOBJECT
                                     )),
                    
                    }
    
    request_queue_size = 100
    allow_reuse_address = True
    connected_clients = []
    connected_clients_by_addr = {}
    handshake = True
    dispatch_func = None
    recvfile_func = None
    
    def __init__(self, server_address, RequestHandlerClass, privkey_path, selfsigned_path):
        
        self.__gobject_init__()
        
        self.logger = logging.getLogger('net:Server')
        
        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass
        
        self.session = gnutls.ServerSessionFactory(privkey_path, selfsigned_path)
        
        self.server_bind()
        self.server_activate()
    
    def server_bind(self):
        
        if self.allow_reuse_address:
            self.session.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.session.bind(self.server_address)
        self.server_address = self.session.getsockname()
    
    def server_activate(self):
        """
            Activate the server
        """
        
        self.session.listen(self.request_queue_size)
    
    def server_close(self):
        
        self.session.shutdown()
        self.session.close()

    def fileno(self):
        return self.session.fileno()
    
    def disconnect_session(self, session):
        
        session.close()
        
        if session in self.connected_clients:
            self.connected_clients.remove(session)
        
        address = session.client_address
        
        if self.connected_clients_by_addr.has_key(address[0]):
            if session in self.connected_clients_by_addr[address[0]]:
                self.connected_clients_by_addr[address[0]].remove(session)
        
        if not session.disconnected:
            self.emit('disconnected', address, session.hash_id)
        
        session.disconnected = True
    
    def process_connection(self, request, client_address):
        try:
            self.finish_request(request, client_address)
            self.close_connection(request)
            
        except:
            self.handle_error(request, client_address)
            self.close_connection(request)
    
    def finish_request(self, request, client_address):
        
        session = self.RequestHandlerClass(request, client_address, self)
        self.connected_clients.append(session)
        
        if not self.connected_clients_by_addr.has_key(client_address[0]):
            self.connected_clients_by_addr[client_address[0]] = []
        
        self.connected_clients_by_addr[client_address[0]].append(session)
        
    def handle_connection(self, server_session, flags):
        
        if flags & gobject.IO_ERR:
            print "Flags IO_ERR"
            return False
        
        if flags & gobject.IO_HUP:
            print "Flags IO_HUP"
            return False
        
        try:
            session, client_address = server_session.accept()
        except socket.error:
            return True
        
        try:
            self.process_connection(session, client_address)
        except:
            traceback.print_exc()
            self.handle_error(session, client_address)
            self.close_connection(session)
        
        return True
    
    def close_connection(self, request):
        """Called to clean up an individual request."""
        request.close()
    
    def handle_error(self, request, client_address):
        print '-' * 40
        print 'Exception happened during processing of request from',
        print client_address
        traceback.print_exc() # XXX But this goes to stderr!
        print '-' * 40
    
    def serve_forever(self):
        self.io_watch_tag = gobject.io_add_watch(self.session,
                                                 gobject.IO_IN | gobject.IO_ERR | gobject.IO_HUP,
                                                 self.handle_connection)
    
    def serve_stop(self):
        self.closeall_connections()
        
        if self.io_watch_tag:
            gobject.source_remove(self.io_watch_tag)
        
        self.close_connection(self.session)
    
    def closeall_connections(self):
        for con in self.connected_clients:
            con.close()
