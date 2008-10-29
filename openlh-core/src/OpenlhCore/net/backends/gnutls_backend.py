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

import socket

import gnutls
import gnutls.crypto
import gnutls.connection
from gnutls import __version__ as GNUTLS_VERSION

class ServerSession:
    def __init__(self, session):
        self.session = session
    
    def __getattr__(self, name):
        ## Generic wrapper for the underlying socket methods and attributes
        return getattr(self.session, name)

class ServerSessionFactory:
    
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    
    def __init__(self, privkey_path, selfsigned_path):
        
        self.cert = gnutls.crypto.X509Certificate(open(selfsigned_path).read())
        self.key = gnutls.crypto.X509PrivateKey(open(privkey_path).read())
        
        self.cred = gnutls.connection.X509Credentials(self.cert, self.key)
        
        self.socket = socket.socket(self.address_family, self.socket_type)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.session = gnutls.connection.ServerSessionFactory(self.socket,
                                                                 self.cred)
    
    def __getattr__(self, name):
        ## Generic wrapper for the underlying socket methods and attributes
        return getattr(self.session, name)
    
    def accept(self):
        new_session, address = self.session.accept()
        session = ServerSession(new_session)
        return (session, address)

class ClientSession:
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    
    def __init__(self, privkey_path, selfsigned_path):
    
        self.cert = gnutls.crypto.X509Certificate(open(selfsigned_path).read())
        self.key = gnutls.crypto.X509PrivateKey(open(privkey_path).read())
        
        self.cred = gnutls.connection.X509Credentials(self.cert, self.key)
        
        self.socket = socket.socket(self.address_family, self.socket_type)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.session = gnutls.connection.ClientSession(self.socket, self.cred)
    
    def __getattr__(self, name):
        ## Generic wrapper for the underlying socket methods and attributes
        return getattr(self.session, name)
    