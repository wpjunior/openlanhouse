#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  N3RD3X <n3rd3x@linuxmail.org>
#  Gabriel Falcão gabriel@nacaolivre.org
#
#  Open LanHouse - Copyright (c) 2007-2008.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import pygtk
pygtk.require('2.0')
import logging

import gtk
import gtk.glade

from OpenLH.core.constants import *
from OpenLH.core import config
from OpenLH.core.ui import dialogs

class Prefs:
    def __init__(self, title=None, Parent=None):
        
        self.logger = logging.getLogger('client.prefs')
        
        self.logger.debug('Building dialog')
        
        self.xml = self.create_widgets(CLIENT_PREFS_GLADE)
        self.config = config.config(CONFIG_CLIENT)
        self.data = {}
        self.data['server'] = None
        self.get_configs()
        self.xml.signal_autoconnect(self)
        """"
        if os.name == 'posix':
            if os.getuid() != 0: #CHECK ROOT
                self.logger.critical('Operation not permitted')
                self.prefs.set_sensitive(False)
                text = ERR_013 % 'openlh-client-prefs'
                dialogs.ok_only(text, ICON=gtk.MESSAGE_ERROR)
                sys.exit(1)
        """
        if Parent:
            self.logger.debug('Seting parent window')
            self.prefs.set_transient_for(Parent)
        
        if title:
            self.prefs.set_title(title)
        
        
    def create_widgets(self, glade_file):
        
        xml = gtk.glade.XML(glade_file)
        
        self.prefs = xml.get_widget('prefs')
        self.alignment = xml.get_widget('alignment')
        self.wall_local = xml.get_widget('wall_local')
        self.check_local = xml.get_widget('check_local')
        self.wall_default = xml.get_widget('wall_default')
        self.server_entry = xml.get_widget('server_entry')
        
        self.wallpaper_dialog = dialogs.ImageChooserDialog(
                                on_response_ok=self.set_wallpaper)
        
        self.wallbnt = gtk.FileChooserButton(dialog = self.wallpaper_dialog)
        self.wallbnt.set_sensitive(False)
        self.alignment.add(self.wallbnt)
        
        return xml
        
        
    def get_configs(self):
        
        self.logger.info('Reading Configurations from %s' % CONFIG_CLIENT)
        
        if self.config.check_option(*CONFIG_011):
            tmpdata = self.config.get_option(*CONFIG_011)
            self.data['server'] = tmpdata
            self.server_entry.set_text(tmpdata)
        
        if self.config.get_option(*CONFIG_012) == 'on':
            self.check_local.set_active(True)
        
        if self.config.get_option(*CONFIG_013) == 'on':
            self.wall_local.set_active(True)
            self.wallbnt.set_sensitive(True)
            
            if self.config.check_option(*CONFIG_014):
                filename = unicode(self.config.get_option(*CONFIG_014))
                if os.path.exists(filename):
                    print self.wallpaper_dialog.set_filename(filename)
                    print self.wallpaper_dialog.select_filename(filename)
    
    def server_changed(self, obj, event):
        
        text = obj.get_text()
        
        if self.data['server'] != text:
            self.data['server'] = text
            self.config.set_option(CONFIG_011[0], CONFIG_011[1], text)
    
    def on_check_local_toggled(self, obj):
        opt = ['off','on'][obj.get_active()]
        self.config.set_option(CONFIG_012[0], CONFIG_012[1], opt)
        
    def on_wall_default_toggled(self, obj):
        if obj.get_active():
            self.config.set_option(CONFIG_013[0], CONFIG_013[1], 'off')
            self.wallbnt.set_sensitive(False)
    
    def on_wall_local_toggled(self, obj):
        if obj.get_active():
            self.config.set_option(CONFIG_013[0], CONFIG_013[1], 'on')
            self.wallbnt.set_sensitive(True)
    
    def on_mngbnt_clicked(self, obj):
        print 'on_mngbnt_clicked'
    
    def set_wallpaper(self, obj, path):
        self.config.set_option(CONFIG_014[0], CONFIG_014[1], path)
        