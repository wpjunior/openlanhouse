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

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import time
import gobject
import tempfile
import time
import thread
import urllib2

from hashlib import sha1 as sha
from BaseHTTPServer import BaseHTTPRequestHandler
from OpenlhClient.globals import *
_ = gettext.gettext
responses = BaseHTTPRequestHandler.responses
del BaseHTTPRequestHandler

def generate_id_bytime():
    
    cur_time = time.time()
    hash = sha(str(cur_time))
    
    return hash.hexdigest()

class HttpDownload(gobject.GObject):
    
    __gsignals__ = {'done': (gobject.SIGNAL_RUN_FIRST,
                             gobject.TYPE_NONE,
                             (gobject.TYPE_PYOBJECT,)),
                   }
    
    CHUNKSIZE = 4096
    THROTTLE_SLEEP_TIME = 0.01

    def __init__ (self):
        
        self.__gobject_init__()
        
        self.url = None
        self.directory = None
        self.fn = None
        self.done = False
        self.err = None
        self.bytes_read = -1
        self.content_length = 0
        self.cancelled = False
        self.verbose = False

    def get_error_msg_from_error(self, err):
        msg = _("Unexpected error of type %s") % type(err)
        
        try:
            raise err
        except urllib2.HTTPError, e:
            if e.code == 403:
                msg = _("Access to this file is forbidden")
            
            elif e.code == 404:
                msg = _("File not found on server")
                
            elif e.code == 500:
                msg = _("Internal server error, try again later")
                
            elif e.code == 503:
                msg = _("The server could not process the request due to " \
                        "high server load, try again later")
                
            else:
                try:
                    m = responses[e.code]
                except KeyError:
                    m = _("Unknown Error")
                msg = _("Server error %u: %s") % (e.code, m)
            
        except urllib2.URLError, e:
            msg = _("Failed to connect to server: %s") % e.reason[1]
            
        except IOError, e:
            if e.filename and e.strerror:
                msg = _("File error for '%s': %s") % (e.filename, e.strerror)
                
            elif e.strerror:
                msg = _("File error: %s") % e.strerror
                
            elif e.filename:
                msg = _("File error for '%s'") % e.filename
                
            elif e.errno:
                msg = _("Unknown file error %d") % e.errno
                
            else:
                msg = _("Unknown file error %d") % e.errno

        return msg

    """ Iterates the default GLib main context until the download is done """
    def run(self, url, directory, fn, message=None):
        
        if self.url:
            return _("Download already in progress")
        
        self.url = url
        self.directory = directory
        self.fn = fn
        self.done = False
        self.err = None
        self.bytes_read = -1
        self.content_length = 0
        self.cancelled = False

        thread.start_new_thread(self.thread_func, ())

        timeout_id = gobject.timeout_add(500, self.update_progress)

        self.update_progress()

      # Don't try to be smart and block here using mayblock=True, it won't work
        while not self.done:
            gobject.main_context_default().iteration(False)

        gobject.source_remove(timeout_id)

      # Update to 'finished' state
        self.update_progress()
        while gobject.main_context_default().pending():
            gobject.main_context_default().iteration(False)

      # Reset state
        self.url = None
        self.directory = None
        self.fn = None
        self.done = False
        self.bytes_read = -1
        self.content_length = 0

        return self.err

    """ Called from the context of the main GUI thread """
    def update_progress(self):
        if self.verbose:
            if self.bytes_read < 0:
                print "Connecting to server"
                
            elif self.bytes_read == 0:
                print "Connected to server"
                
            elif self.content_length > 0:
                print "Bytes read: %.1f (%.1f%%)" %                    \
                      (self.bytes_read / 1024.0,                       \
                       self.bytes_read * 100.0 / self.content_length)
                       
            else:
                print "Bytes read: %.1f" % (self.bytes_read / 1024.0)

        return not self.done

    """ Thread where all the downloading and file writing happens """
    def thread_func(self):

        tmpfile_path = None

      # First, see if we can resolve the URL at all and connect to the host
        try:
            self.bytes_read = -1
            res = urllib2.urlopen(self.url)
            self.bytes_read = 0
            time.sleep(self.THROTTLE_SLEEP_TIME)

            try:
                self.content_length = int(res.info()['Content-Length'])
            except KeyError:
                self.content_length = 0

          # Make sure the directory exists (ignore exception thrown if it
          # already exists, mkstemp will throw an exception later if there
          # is really a problem)
            try:
                os.makedirs(self.directory)
            except:
                pass

            # Now create a temp file there
            tmpfile_handle, tmpfile_path = tempfile.mkstemp('.incomplete',\
                                                            'openlh-client')

            while not self.cancelled:
                data = res.read(self.CHUNKSIZE)
                if data and len(data):
                    self.bytes_read += len(data)
                    os.write(tmpfile_handle, data)
                    # give GUI thread a chance to show progress
                    time.sleep(self.THROTTLE_SLEEP_TIME)
                else:
                    break

          # Now rename the temporary file to the desired file name
            if self.cancelled:
                try:
                    os.remove(tmpfile_path)
                except:
                    pass
            else:
                os.rename(tmpfile_path, os.path.join(self.directory, self.fn))

        except (urllib2.HTTPError, urllib2.URLError, IOError), e:
            self.err = self.get_error_msg_from_error (e)
            
            if tmpfile_path:
                try:
                    os.remove(tmpfile_path)
                except:
                    pass
                    
        else:
            self.err = None

      # Finished (one way or another), stop the thread
        self.done = True
        thread.exit()