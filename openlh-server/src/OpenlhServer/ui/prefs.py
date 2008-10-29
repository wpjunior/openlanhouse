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

import gtk
import gconf

from os.path import exists
from OpenlhServer.globals import *
from OpenlhServer.ui.dialogs import image_chooser_button
from OpenlhServer.ui.utils import get_gtk_builder

class Prefs:
    def __init__(self, title=None, Parent=None):
        
        self.gconf_client = gconf.client_get_default()
        self.gconf_client.add_dir('/apps/openlh-server',
                                  gconf.CLIENT_PRELOAD_NONE)
        
        self.xml = get_gtk_builder('prefs')
        self.prefs = self.xml.get_object('prefs')
        
        self.background_chooser = image_chooser_button()
        self.logo_chooser = image_chooser_button()
        
        background_chooser_btn = self.background_chooser.get_children()[0]
        logo_chooser_btn = self.logo_chooser.get_children()[0]
        
        background_chooser_btn.connect('focus-in-event',
                                       self.background_chooser_focus)
        background_chooser_btn.connect('focus-out-event',
                                       self.background_chooser_focus)
        
        logo_chooser_btn.connect('focus-in-event', self.logo_chooser_focus)
        logo_chooser_btn.connect('focus-out-event', self.logo_chooser_focus)
        
        self.xml.get_object('lock_box').attach(self.background_chooser, 1, 2, 0, 1,
                    xoptions=gtk.FILL|gtk.EXPAND, xpadding=0, ypadding=0)
        
        self.xml.get_object('lock_box').attach(self.logo_chooser, 1, 2, 1, 2,
                    xoptions=gtk.FILL|gtk.EXPAND, xpadding=0, ypadding=0)
        
        self.background_chooser.connect('file-activated', self.file_activated)
        
        self.background_chooser.show()
        self.logo_chooser.show()
        
        self.get_configs()
        
        if Parent:
            self.prefs.set_transient_for(Parent)
        
        if title:
            self.prefs.set_title(title)
        
        self.xml.connect_signals(self)
        
    def get_configs(self):
        
        data = {}
        
        data['lan_name'] = self.gconf_client.get_string('/apps/openlh-server/name')
        data['admin_email'] = self.gconf_client.get_string('/apps/openlh-server/admin_email')
        data['currency'] = self.gconf_client.get_string('/apps/openlh-server/currency')
        data['price.hour'] = self.gconf_client.get_float('/apps/openlh-server/price_per_hour')
        data['custom_welcome_msg'] = self.gconf_client.get_string('/apps/openlh-server/welcome_msg')
        
        for name in 'lan_name', 'admin_email', 'currency':
            if data[name]:
                self.xml.get_object(name).set_text(data[name])
        
        if data['price.hour']:
            self.xml.get_object("price_hour").set_value(data['price.hour'])
        
        if self.gconf_client.get_bool('/apps/openlh-server/login_suport'):
            self.xml.get_object('machine_login_suport').set_active(True)
        
        if self.gconf_client.get_bool('/apps/openlh-server/ticket_suport'):
            self.xml.get_object('ticket_suport').set_active(True)
        
        if self.gconf_client.get_bool('/apps/openlh-server/default_welcome_msg'):
            self.xml.get_object('default_welcome_msg').set_active(True)
        else:
            self.xml.get_object('custom_welcome_msg').set_active(True)
            self.xml.get_object('custom_msg_entry').set_sensitive(True)
        
        if data['custom_welcome_msg']:
            self.xml.get_object('custom_msg_entry').set_text(data['custom_welcome_msg'])
        
        if self.gconf_client.get_bool('/apps/openlh-server/background'):
            self.xml.get_object('background_bnt').set_active(True)
        else:
            self.background_chooser.set_sensitive(False)
        
        if self.gconf_client.get_bool('/apps/openlh-server/logo'):
            self.xml.get_object('logo_bnt').set_active(True)
        else:
            self.logo_chooser.set_sensitive(False)
        
        self.background_path = self.gconf_client.get_string('/apps/openlh-server/background_path')
        self.logo_path = self.gconf_client.get_string('/apps/openlh-server/logo_path')
        
        if self.background_path and exists(self.background_path):
            self.background_chooser.set_filename(self.background_path)
        
        if self.logo_path and exists(self.logo_path):
            self.logo_chooser.set_filename(self.logo_path)
        
    def lan_name_changed(self, obj, event):
        self.gconf_client.set_string('/apps/openlh-server/name',
                                     obj.get_text())
    
    def admin_email_changed(self, obj, event):
        self.gconf_client.set_string('/apps/openlh-server/admin_email',
                                     obj.get_text())
    
    def on_currency_focus_out_event(self, obj, event):
        self.gconf_client.set_string('/apps/openlh-server/currency',
                                     obj.get_text())
    
    def on_price_hour_focus_out_event(self, obj, event):
        self.gconf_client.set_float('/apps/openlh-server/price_per_hour',
                                    obj.get_value())
        
    def on_machine_login_suport_toggled(self, obj):
        self.gconf_client.set_bool('/apps/openlh-server/login_suport',
                                   obj.get_active())
    
    def on_ticket_suport_toggled(self, obj):
        self.gconf_client.set_bool('/apps/openlh-server/ticket_suport',
                                   obj.get_active())
        
    def on_custom_welcome_msg_toggled(self, obj):
        status = obj.get_active()
        self.xml.get_object('custom_msg_entry').set_sensitive(status)
        self.gconf_client.set_bool('/apps/openlh-server/default_welcome_msg',
                                   not(obj.get_active()))
    
    def on_custom_welcome_msg_changed(self, obj, event):
        self.gconf_client.set_string('/apps/openlh-server/welcome_msg',
                                     obj.get_text())
    
    def background_bnt_toggled_cb(self, obj):
        status = obj.get_active()
        self.gconf_client.set_bool('/apps/openlh-server/background',
                                   status)
        self.background_chooser.set_sensitive(status)
    
    def on_logo_bnt_toggled(self, obj):
        status = obj.get_active()
        self.gconf_client.set_bool('/apps/openlh-server/logo',
                                   status)
        self.logo_chooser.set_sensitive(status)
        
    def file_activated(self, obj):
        print 'file_activated'
    
    def background_chooser_focus(self, obj, event):
        
        filename = self.background_chooser.get_filename()
        
        if self.background_path != filename:
            self.background_path = filename
            self.gconf_client.set_string('/apps/openlh-server/background_path',
                                         filename)
        
    def logo_chooser_focus(self, obj, event):
        print "logo"
        filename = self.logo_chooser.get_filename()
        
        if self.logo_path != filename:
            self.logo_path = filename
            self.gconf_client.set_string('/apps/openlh-server/logo_path',
                                         filename)
