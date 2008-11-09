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

from os.path import exists
from OpenlhServer.globals import *
from OpenlhServer.ui.dialogs import image_chooser_button
from OpenlhServer.ui.utils import get_gtk_builder
from OpenlhCore.ConfigClient import get_default_client

class Prefs:
    def __init__(self, title=None, Parent=None):
        
        self.conf_client = get_default_client()
                
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
        
        data['lan_name'] = self.conf_client.get_string('name')
        data['admin_email'] = self.conf_client.get_string('admin_email')
        data['currency'] = self.conf_client.get_string('currency')
        data['price.hour'] = self.conf_client.get_float('price_per_hour')
        data['custom_welcome_msg'] = self.conf_client.get_string('welcome_msg')
        
        for name in 'lan_name', 'admin_email', 'currency':
            if data[name]:
                self.xml.get_object(name).set_text(data[name])
        
        if data['price.hour']:
            self.xml.get_object("price_hour").set_value(data['price.hour'])
        
        if self.conf_client.get_bool('login_suport'):
            self.xml.get_object('machine_login_suport').set_active(True)
        
        if self.conf_client.get_bool('ticket_suport'):
            self.xml.get_object('ticket_suport').set_active(True)
        
        if self.conf_client.get_bool('default_welcome_msg'):
            self.xml.get_object('default_welcome_msg').set_active(True)
        else:
            self.xml.get_object('custom_welcome_msg').set_active(True)
            self.xml.get_object('custom_msg_entry').set_sensitive(True)
        
        if data['custom_welcome_msg']:
            self.xml.get_object('custom_msg_entry').set_text(data['custom_welcome_msg'])
        
        if self.conf_client.get_bool('background'):
            self.xml.get_object('background_bnt').set_active(True)
        else:
            self.background_chooser.set_sensitive(False)
        
        if self.conf_client.get_bool('logo'):
            self.xml.get_object('logo_bnt').set_active(True)
        else:
            self.logo_chooser.set_sensitive(False)
        
        self.background_path = self.conf_client.get_string('background_path')
        self.logo_path = self.conf_client.get_string('logo_path')
        
        if self.background_path and exists(self.background_path):
            self.background_chooser.set_filename(self.background_path)
        
        if self.logo_path and exists(self.logo_path):
            self.logo_chooser.set_filename(self.logo_path)
        
    def lan_name_changed(self, obj, event):
        self.conf_client.set_string('name',
                                     obj.get_text())
    
    def admin_email_changed(self, obj, event):
        self.conf_client.set_string('admin_email',
                                     obj.get_text())
    
    def on_currency_focus_out_event(self, obj, event):
        self.conf_client.set_string('currency',
                                     obj.get_text())
    
    def on_price_hour_focus_out_event(self, obj, event):
        self.conf_client.set_float('price_per_hour',
                                    obj.get_value())
        
    def on_machine_login_suport_toggled(self, obj):
        self.conf_client.set_bool('login_suport',
                                   obj.get_active())
    
    def on_ticket_suport_toggled(self, obj):
        self.conf_client.set_bool('ticket_suport',
                                   obj.get_active())
        
    def on_custom_welcome_msg_toggled(self, obj):
        status = obj.get_active()
        self.xml.get_object('custom_msg_entry').set_sensitive(status)
        self.conf_client.set_bool('default_welcome_msg',
                                   not(obj.get_active()))
    
    def on_custom_welcome_msg_changed(self, obj, event):
        self.conf_client.set_string('welcome_msg',
                                     obj.get_text())
    
    def background_bnt_toggled_cb(self, obj):
        status = obj.get_active()
        self.conf_client.set_bool('background',
                                   status)
        self.background_chooser.set_sensitive(status)
    
    def on_logo_bnt_toggled(self, obj):
        status = obj.get_active()
        self.conf_client.set_bool('logo',
                                   status)
        self.logo_chooser.set_sensitive(status)
        
    def file_activated(self, obj):
        print 'file_activated'
    
    def background_chooser_focus(self, obj, event):
        
        filename = self.background_chooser.get_filename()
        
        if self.background_path != filename:
            self.background_path = filename
            self.conf_client.set_string('background_path',
                                         filename)
        
    def logo_chooser_focus(self, obj, event):
        print "logo"
        filename = self.logo_chooser.get_filename()
        
        if self.logo_path != filename:
            self.logo_path = filename
            self.conf_client.set_string('logo_path',
                                         filename)
