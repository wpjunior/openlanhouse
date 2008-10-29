#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008 Wilson Pinto Júnior (N3RD3X) <n3rd3x@guake-terminal.org>
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

import gtk
from OpenlhServer.globals import *

try:
    import pynotify
    notifysuport = True
except:
    pynotify = None
    notifysuport = False

class Tray:
    def __init__(self, name, icon=None, icon_name=None):
        """
            Construct Tray and Pynotify
        """
        
        self.notifysuport = notifysuport
        self.notify = pynotify #FIX
        
        if self.notifysuport:
            if not pynotify.is_initted():
                if not pynotify.init(name):
                    self.notifysuport = False
        
        if icon:
            try:
                self.icon = gtk.status_icon_new_from_pixbuf(icon)
                self.icon.set_tooltip(name)
                self.iconsuport = True
            except:
                self.iconsuport = False

        elif icon_name:
            try:
                self.icon = gtk.status_icon_new_from_icon_name(icon_name)
                self.icon.set_tooltip(name)
                self.iconsuport = True
            except:
                self.iconsuport = False
        
        else:
            self.iconsuport = False
    
    def notify_msg(self, title, msg, timeout=8000,
                  icon=gtk.STOCK_DIALOG_INFO, in_status_icon=True):
        """
            Create notify widget
        """
        
        if self.notifysuport:
            notify = pynotify.Notification(title, msg, icon)
            
            if timeout:
                notify.set_timeout(timeout)
                        
            if self.iconsuport and in_status_icon:
                notify.attach_to_status_icon(self.icon)
            
            return notify
        #else:
            #print ERR_003 #TODO: USE LOGGING
