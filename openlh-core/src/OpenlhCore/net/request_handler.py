#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008 Wilson Pinto Júnior <wilsonpjunior@gmail.com>
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

import traceback
import logging

from os import path as ospath
from threading import RLock
from OpenlhCore.utils import DictLimited

from xmlrpclib import loads as xmlpickler_loads
from xmlrpclib import dumps as xmlpickler_dumps

from OpenlhCore.net.response import Response
from OpenlhCore.net.constants import *

class RequestHandler(gobject.GObject):
    
    rbufsize = -1
    wbufsize = 0
    checking = False
    currid = 1
    
    closed = False
    disconnected = False
    hash_id = None
    io_session_handler_id = 0
    
    current_id = None
    current_size = None
    current_type = None
    current_size_remaining = None
    current_data = None
    current_method = None
    
    def __init__(self, session, client_address, server):
        
        self.__gobject_init__()
        
        self.session = session
        self.client_address = client_address
        self.server = server
        
        self.send_lock = RLock()
        self.open_responses = DictLimited(limit=10)
        
        self.logger = logging.getLogger('%s:%s' % client_address)
        
        try:
            self.setup()
            self.handshake()
            gobject.timeout_add(5000, self.check_hash_id)
            self.io_session_handler_id = gobject.io_add_watch(self.session,
                                                              gobject.IO_IN | gobject.IO_ERR | gobject.IO_HUP,
                                                              self.handler_io)
            
        except:
            traceback.print_exc()
            self.close()
        
        finally:
            sys.exc_traceback = None
    
    def setup(self):
        self.rfile = self.session.makefile('rb', self.rbufsize)
        self.wfile = self.session.makefile('wb', self.wbufsize)
    
    def handshake(self):
        self.session.handshake()
    
    def close(self):
        """
            Close Connection
        """
        self.listen = False
        
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
        
        self.closed = True
        self.logger.info('connection closed')
    
    def send_response(self, id, response):
        """
            Send reponse to peer
        """
        
        try:
            output = xmlpickler_dumps((response,), methodresponse=1)
            head = BEGIN_XMLRESPONSE_HEADER % (id, len(output))
            
            self.send_lock.acquire() #acquire thread lock
            
            self.session.send(head)
            self.session.send(output)
            self.session.send(END_XMLRESPONSE_HEADER)
        
        except Exception, error:
            traceback.print_exc()
            self.logger.error(error)
        
        self.send_lock.release() #release thread lock
    
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
        
        self.send_lock.acquire() #acquire thread lock
        
        try:
            self.session.send(head)
            self.session.send(xmlout)
            self.session.send(END_XMLREQUEST_HEADER)
            has_error = False
        except Exception, error:
            has_error = True
            self.logger.error(error)
            traceback.print_exc()
            
        self.send_lock.release() #release thread lock
        
        if has_error:
            return
        
        response = Response(self.currid)
        self.open_responses[self.currid] = response
        self.currid += 1
        
        return response
            
    def handle_headers(self, data):
        """
            Handler header and return missing data
        """
        
        #Response Header
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
        
        #Response End
        elif (self.current_type == XMLRESPONSE_TYPE and
                        data.startswith(END_XMLRESPONSE_HEADER)):
            
            self.check_and_alert_size_remaining()
            
            outdata = ''.join(self.current_data)
            
            self.current_type = None
            self.current_data = []
            id = self.current_id
            
            try:
                response = xmlpickler_loads(outdata)[0][0]
                
                if self.open_responses.has_key(id):
                    self.open_responses[id].set_value(response)
                    self.open_responses.pop(id)
            
            except Exception, error:
                self.logger.error(error)
                traceback.print_exc()
            
            data = data[len(END_XMLRESPONSE_HEADER):]
            
            return data
            
        #Request Header
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
                    
            except Exception, error:
                self.logger.error(error)
                traceback.print_exc()
                data = ""
            
            return data
        
        #End Request
        elif (self.current_type == XMLREQUEST_TYPE and
                        data.startswith(END_XMLREQUEST_HEADER)):
            
            self.check_and_alert_size_remaining()
            
            outdata = ''.join(self.current_data)
            self.current_type = None
            self.current_data = []
            id = self.current_id
            
            params, method = xmlpickler_loads(outdata)
            
            if self.server.dispatch_func:
                response = self.server.dispatch_func(self.hash_id, 
                                                    method, params)
            
            else:
                response = None
            
            self.send_response(id, response)
            data = data[len(END_XMLREQUEST_HEADER):]
            
            return data
        
    def handle_data(self, data, client_address):
        """
            Handle data received
        """
        
        if not self.current_type:
            self.logger.debug('error no type defined')
            return
        
        self.current_data.append(data[:self.current_size_remaining])
        self.current_size_remaining -= len(data[:self.current_size_remaining])
    
    def handler_io(self, session, flags):
        """
            Handler all data received
        """
        
        if flags & gobject.IO_ERR:
            print "Flags IO_ERR"
            self.close_session()
            return False
        
        if flags & gobject.IO_HUP:
            print "Flags IO_HUP"
            self.close_session()
            return False
        
        try:
            data = session.recv(1024)
            
            if data == 0 or data == '' or data == 'CLOSE':
                raise IOError('Disconnected from client')
            
            # Identification packet
            if data.startswith('-----HASH_ID'):
                m = HashIDRegex.match(data)
                
                if m:
                    hash_id = m.group('hash_id')
                    data = m.group('data')
                else:
                    hash_id = None
                    data = ""
                
                if hash_id and not self.hash_id:
                    self.hash_id = hash_id
                    self.server.emit('connected', self.client_address,
                                     self, self.hash_id)
            
            #headers
            if data.startswith('-----'):
                try:
                    data = self.handle_headers(data)
                except:
                    traceback.print_exc()
                    data = ""
            
            #finally data
            if data:
                self.handle_data(data, self.client_address)
            
            return True
        
        except Exception, error:
            self.logger.error(str(error))
            self.close_session()
            return False
    
    def check_hash_id(self):
        """
            Check hash id after 5 seconds after connection up
        """
        if not self.hash_id:
            self.logger.error('Close Connection: Because no sent hash_id')
            self.close_session()
    
    def close_session(self):
        """
            Close Socket Session
        """
        self.server.disconnect_session(self)
    
    def check_and_alert_size_remaining(self):
        if self.current_size_remaining != 0:
            self.logger.warning('size_remaining != 0, size_remaing = %d' % self.current_size_remaining)
    
