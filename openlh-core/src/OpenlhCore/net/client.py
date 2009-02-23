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

import sys
import re
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

from xmlrpclib import loads as xmlpickler_loads
from xmlrpclib import dumps as xmlpickler_dumps

from OpenlhCore.net.response import Response
from OpenlhCore.net.constants import *

from os import path as ospath
from threading import RLock

class NetClient(gobject.GObject):
    """
        Network Client Class
    """
    __gsignals__ = {'connected':(gobject.SIGNAL_RUN_FIRST,
                                     gobject.TYPE_NONE,
                                     (gobject.TYPE_STRING,)),
                    
                    'disconnected':(gobject.SIGNAL_RUN_FIRST,
                                     gobject.TYPE_NONE,
                                     ()),
                    
                    }
    
    rbufsize = -1
    wbufsize = 0
    receive = False
    handshake = True
    
    current_id = None
    current_size = None
    current_type = None
    current_size_remaining = None
    current_data = None
    current_method = None
    
    currid = 1
    
    dispatch_func = None
    recvfile_func = None
    
    open_responses = {}
    io_session_handler_id = 0
    
    def __init__(self, server, port, cert_path, key_path, hash_id):
        
        self.__gobject_init__()
        
        self._server = server
        self._port = port
        self.hash_id = hash_id
        
        self.send_lock = RLock()
        self.logger = logging.getLogger('net:Client')
        
        self.session = gnutls.ClientSession(key_path, cert_path)
        
    def handle_headers(self, data):
        """
            Handler header and return missing data
        """
        
        #Begin XMLRESPONSE
        if data.startswith('-----BEGIN XMLRESPONSE'):
            try:
                out = XMLResponseRegex.match(data)
                
                if out:
                    self.current_id = int(out.group('id'))
                    self.current_size = int(out.group('size'))
                    self.current_type = XMLRESPONSE_TYPE
                    self.current_size_remaining = self.current_size
                    self.current_data = []
                    data = out.group('data')
                else:
                    data = ""
            
            except:
                traceback.print_exc()
                data = ""
            
            return data
        
        #End XMLRESPONSE
        elif (self.current_type == XMLRESPONSE_TYPE and
                                data.startswith(END_XMLRESPONSE_HEADER)):
            
            self.check_and_alert_size_remaining()
            
            outdata = ''.join(self.current_data)
            
            self.current_type = None
            self.current_data = []
            
            response = xmlpickler_loads(outdata)[0][0]
            
            if self.open_responses.has_key(self.current_id):
                self.open_responses[self.current_id].set_value(response)
                self.open_responses.pop(self.current_id)
            
            data = data[len(END_XMLRESPONSE_HEADER):]
            
            return data
                
       #Begin XMLREQUEST
        elif data.startswith('-----BEGIN XMLREQUEST'):
            
            try:
                out = XMLRequestRegex.match(data)
                
                if out:
                    self.current_id = int(out.group('id'))
                    self.current_size = int(out.group('size'))
                    self.current_type = XMLREQUEST_TYPE
                    self.current_size_remaining = self.current_size
                    self.current_data = []
                    
                    data = out.group('data')
                else:
                    data = ""
            
            except:
                traceback.print_exc()
                data = ""
            
            return data
        
        #End XMLREQUEST
        elif (self.current_type == XMLREQUEST_TYPE and
                                data.startswith(END_XMLREQUEST_HEADER)):
            
            self.check_and_alert_size_remaining()
            
            outdata = ''.join(self.current_data)
            self.current_type = None
            self.current_data = []
            id = self.current_id
            
            params, method = xmlpickler_loads(outdata)
            
            if self.dispatch_func:
                response = self.dispatch_func(method, params)
            
            else:
                response = None
            
            self.send_response(id, response)
            
            data = data[len(END_XMLREQUEST_HEADER):]
            
            return data
            
    def handle_data(self, data):
        """
            Handle data received
        """
        
        if not self.current_type:
            self.logger.debug('error no type defined')
            return
            
        self.current_data.append(data)
        self.current_size_remaining -= len(self.current_data[-1])
    
    def handle_io(self, session, flags):
        """
            Handler all data received
        """
        
        if flags & gobject.IO_ERR:
            print "Flags IO_ERR"
            return False
        
        if flags & gobject.IO_HUP:
            print "Flags IO_HUP"
            return False
        
        try:
            data = self.session.recv(1024)
            
            if data == 0 or data == '' or data == 'CLOSE':
                raise IOError('Disconnected from server')
            
            #headers
            if data.startswith('-----'):
                try:
                    data = self.handle_headers(data)
                except Exception, error:
                    traceback.print_exc()
                    data = ""
            
            #finally data
            if data:
                self.handle_data(data)
            
            return True
            
        except Exception, error:
            self.logger.error(error)
            self.stop()
            
            return False
        
    def start(self):
        """
            Start Connection in server
        """
        try:
            self.session.connect((self._server, self._port))
            
            if self.handshake:
                self.session.handshake()
            
            self.emit('connected', (self._server, self._port))
            
            self.rfile = self.session.makefile('rb', self.rbufsize)
            self.wfile = self.session.makefile('wb', self.wbufsize)
            
            self.send_hash_id() #Send packet identification to server
            self.io_session_handler_id = gobject.io_add_watch(self.session,
                                                              gobject.IO_IN | gobject.IO_ERR | gobject.IO_HUP, 
                                                              self.handle_io)
            
            return True
            
        except Exception, error:
            try:
                (code, msg) = error
            except ValueError:
                msg = str(error)
            
            traceback.print_exc()
            self.logger.error(msg)
            return False
    
    def stop(self):
        """
            Close Connection in Server
        """
        self.logger.info('connection closed')
        self.receive = False
        
        if self.io_session_handler_id:
            gobject.source_remove(self.io_session_handler_id)
        
        try:
            self.session.send('CLOSE')
        except:
            pass
        
        try:
            self.session.shutdown()
        except:
            pass
        
        try:
            self.session.close()
        except:
            pass
        
        try:
            if not self.wfile.closed:
                self.wfile.flush()
        
            self.wfile.close()
            self.rfile.close()
        except:
            pass
        
        self.emit('disconnected')
    
    def send_hash_id(self):
        """
            Send hash_id packet information to server
        """
        self.session.send(HASH_ID_HEADER % self.hash_id)
    
    def request(self, method, params=()):
        """
            Request from peer
            @method:
                name of method requested
            @params:
                tuple params passed to method
        """
        if not isinstance(params, tuple):
            params = (params,)
        
        xmlout = xmlpickler_dumps(params, method)
        size = len(xmlout)
        
        head = BEGIN_XMLREQUEST_HEADER % (self.currid, size)
        self.send_lock.acquire()
        self.session.send(head)
        self.session.send(xmlout)
        self.session.send(END_XMLREQUEST_HEADER)
        
        try:
            self.send_lock.release()
        except:
            pass
        
        response = Response(self.currid)
        self.open_responses[self.currid] = response
        self.currid += 1
        
        return response
    
    def send_response(self, id, response):
        """
            Send Response to peer
        """
        
        try:
            output = xmlpickler_dumps((response,), methodresponse=1)
            head = BEGIN_XMLRESPONSE_HEADER % (id, len(output))
            self.send_lock.acquire()
            self.session.send(head)
            self.session.send(output)
            self.session.send(END_XMLRESPONSE_HEADER)
            
        except Exception, error:
            self.logger.error(error)
        
        try:
            self.send_lock.release()
        except:
            pass
        
    def check_and_alert_size_remaining(self):
        if self.current_size_remaining != 0:
            self.logger.warning('size_remaining != 0, size_remaing = %d' % self.current_size_remaining)
