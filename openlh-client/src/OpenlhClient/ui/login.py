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

import sys
from os import name as osname
import time
import gtk
from gobject import timeout_add, idle_add, source_remove
from time import strftime

from OpenlhClient.globals import *
from OpenlhClient.ui.background import LockScreenWindow
from OpenlhClient.ui.utils import get_gtk_builder
_ = gettext.gettext
HOUR_24_FORMAT = False

(LOGIN_AUTH_NONE,
 LOGIN_AUTH_LOGIN,
 LOGIN_AUTH_TICKET,
 LOGIN_AUTH_ADMIN) = range(4)

(LOGIN_USER, LOGIN_PASSWORD, LOGIN_TICKET) = range(3)

BUTTON_EVENTS = (gtk.gdk.BUTTON_PRESS , gtk.gdk._2BUTTON_PRESS,
                    gtk.gdk._3BUTTON_PRESS, gtk.gdk.BUTTON_RELEASE)

KEY_EVENTS = (gtk.gdk.KEY_PRESS, gtk.gdk.KEY_RELEASE)

class Login:
    
    ticket_suport = False
    login_suport = False
    timeout_connect = 15
    run_interable = False
    selected_auth = LOGIN_AUTH_NONE
    current_widget = LOGIN_USER
    max_ticket_size = 8
    max_nick_size = 14
    iterable_timeout_id = 0
    on_ready = 60
    on_ready_run_interable = False
    
    def __init__(self, main):
        
        xml = get_gtk_builder('login')
        
        self.login = xml.get_object('login')
        
        if osname == "nt": # Change type of login window
            c = self.login.get_children()
            if c:
                w = c[0]
                self.login.remove(w)
                self.login = gtk.Window(gtk.WINDOW_TOPLEVEL)
                self.login.set_decorated(False)
                self.login.set_position(gtk.WIN_POS_CENTER_ALWAYS)
                self.login.add(w)
        
        self.entry = xml.get_object('entry')
        self.image = xml.get_object('image')
        self.label = xml.get_object('label')
        self.title = xml.get_object('title')
        self.okbnt = xml.get_object('okbnt')
        self.againbnt = xml.get_object('againbnt')
        self.warn_msg = xml.get_object('warn_msg')
        self.imagealign = xml.get_object('imagealign')
        self.wm_title = xml.get_object('wm_title')
        self.xml = xml
        self.login_radio_item = self.xml.get_object("login_radio_item")
        self.ticket_radio_item = self.xml.get_object("ticket_radio_item")
        self.admin_radio_item = self.xml.get_object("admin_radio_item")
        self.err_box = self.xml.get_object("err_box")
        
        self.ticket = None
        self.password = None
        self.username = None
        self.running = True
        self.main = main
        
        #Title
        self.xml.get_object("title_eventbox").set_state(gtk.STATE_SELECTED)
        
        #Clock
        self.clock_label = gtk.Label()
        self.clock_item = gtk.MenuItem()
        self.clock_item.add(self.clock_label)
        self.clock_item.set_right_justified(True)
        self.clock_item.show_all()
        self.xml.get_object("menubar").append(self.clock_item)
        self.clock_item.unset_flags(gtk.SENSITIVE)
        self.clock_update()
        self.xml.connect_signals(self)
    
    def clock_update(self):
        if HOUR_24_FORMAT:
            hour_str = strftime(_("%a %b %d, %H:%M"))
        else:
            hour_str = strftime(_("%a %b %d, %l:%M %p"))
        
        self.clock_label.set_text(hour_str)
        timeout_add(1000, self.clock_update)
    
    def on_entry_changed(self, obj):
        if self.current_widget in (LOGIN_USER, LOGIN_PASSWORD):
            self.okbnt.set_sensitive(bool(obj.get_text()))
            
        elif self.current_widget == LOGIN_TICKET:
            self.okbnt.set_sensitive(
                    len(obj.get_text())==self.max_ticket_size)
    
    def on_entry_insert_text(self, obj, new_str, length, position):
        position = obj.get_position()
        
        if self.current_widget == LOGIN_USER:
            if len(obj.get_text()) >= self.max_nick_size:
                obj.stop_emission('insert-text')
                return
                
            if new_str.isalpha() and new_str.isupper():
                obj.stop_emission('insert-text')
                obj.insert_text(new_str.lower(), position)
                idle_add(obj.set_position, position+1)
            
            elif new_str.isdigit() or new_str.islower():
                return
            else:
                obj.stop_emission('insert-text')
        
        elif self.current_widget == LOGIN_TICKET:
            if len(obj.get_text()) >= self.max_ticket_size:
                obj.stop_emission('insert-text')
                return
            
            if new_str.isalpha() and new_str.islower():
                obj.stop_emission('insert-text')
                obj.insert_text(new_str.upper(), position)
                idle_add(obj.set_position, position+1)
                
            elif new_str.isdigit() or new_str.isupper():
                return
            else:
                obj.stop_emission('insert-text')
            
    def activate(self, obj):
        if not self.entry.get_text():
            return
        
        if self.selected_auth == LOGIN_AUTH_LOGIN:
            if self.current_widget == LOGIN_USER:
                self.username = self.entry.get_text()
                self.set_current(LOGIN_PASSWORD)
                self.err_box.set_text("")
                
            elif self.current_widget == LOGIN_PASSWORD:
                self.password = self.entry.get_text()
                self.main.on_login(self.username, self.password)
                self.username = None
                self.password = None
        else:
            self.ticket = self.entry.get_text()
            self.main.on_ticket(self.ticket)
            self.ticket = None
    
    def on_againbnt_clicked(self, obj):
        if self.selected_auth == LOGIN_AUTH_LOGIN:
            self.set_current(LOGIN_USER)
        
    def set_current(self, auth_widget):
        self.current_widget = auth_widget
        
        if auth_widget == LOGIN_USER:
            self.selected_auth = LOGIN_AUTH_LOGIN
            self.label.set_text(_('_Username:'))
            self.entry.set_visibility(True)
            self.againbnt.set_sensitive(False)
        
        if auth_widget == LOGIN_PASSWORD:
            self.selected_auth = LOGIN_AUTH_LOGIN
            self.label.set_text(_('_Password:'))
            self.entry.set_visibility(False)
            self.againbnt.set_sensitive(True)
        
        if auth_widget == LOGIN_TICKET:
            #self.err_box.set_text("")
            self.selected_auth = LOGIN_AUTH_TICKET
            self.label.set_text(_('_Ticket:'))
            self.entry.set_visibility(True)
            self.againbnt.set_sensitive(False)
        
        self.entry.set_text('')
        self.label.set_use_underline(True)
        self.entry.grab_focus()
    
    def set_title(self, title):
        self.title.set_markup("<big><big><big>%s</big></big></big>" % title)
        
    def unlock(self, obj):
        self.background.hide()
    
    def on_entry_event(self, obj, event):
        ##HACK
        ##Redirect key and pointer forbiden events
        if event.type in BUTTON_EVENTS:
            event.button = 1
        
        elif event.type in KEY_EVENTS:
            if event.hardware_keycode == 0x075:
                event.hardware_keycode = 0xFFE9
    
    def lock(self):
        self.background.show()
        
    def run(self):
        gtk.rc_reparse_all()
        screen = gtk.gdk.screen_get_default()
        self.login.realize()
        self.background = LockScreenWindow()
        self.background.show()
        self.background.set_child_window(self.login)
    
    def set_background(self, filepath):
        if filepath:
            self.login.realize()
            self.background.set_background_image(filepath)
        else:
            self.background.set_color('black')
    
    def set_logo(self, logo):
        widget = self.xml.get_object("imagealign")
        
        if logo:
            widget.show() #checar o tamanho do logo
            self.xml.get_object("image").set_from_file(logo)
        else:
            widget.hide()
    
    def set_lock_all(self, status):
        self.entry.set_sensitive(not(status))
        self.label.set_sensitive(not(status))
        self.xml.get_object("mode_menuitem").set_sensitive(not(status))
        
        if status:
            self.label.set_text("")
        else:
            self.set_current(self.current_widget)
    
    def iterable(self):
        if self.timeout_connect != 0:
            if self.run_interable:
                self.timeout_connect -= 1
                self.warn_msg.set_text(_('The connection to the server was ' + 
                                         'lost, trying to connect in %0.2d ' +
                                         'seconds.') % 
                                         (self.timeout_connect + 1))
                
                self.iterable_timeout_id = timeout_add(1000, self.iterable)
                return
            else:
                self.warn_msg.set_text("")
                self.timeout_connect = 15
        else:
            self.run_interable = False
            self.main.reload_network()
            
            if not self.main.netclient.start():
                self.run_interable = True
                self.timeout_connect = 15
                self.iterable_timeout_id = timeout_add(1000, self.iterable)
    
    def on_ready_iterable(self):
        if self.on_ready != 0:
            if self.on_ready_run_interable:
                self.on_ready -= 1
                self.warn_msg.set_text(_('Please wait %0.2d seconds for '
                                         'a new login, Number of attempts '
                                         'has been exceeded') % 
                                         (self.on_ready + 1))
                
                self.iterable_timeout_id = timeout_add(
                                        1000, self.on_ready_iterable)
                return
            else:
                self.warn_msg.set_text("")
                self.on_ready = 60
        else:
            self.set_lock_all(False)
            self.on_ready_run_interable = False
            self.warn_msg.set_text("")
        
    def set_connected(self, status):
        self.set_lock_all(not(status))
        
        if not(status) and not self.background.visible:
            self.lock()
        
        if not status:
            if self.iterable_timeout_id:
                source_remove(self.iterable_timeout_id)
            
            self.run_interable = True
            self.timeout_connect = 15
            self.iterable()
            self.wm_title.set_text(_("OpenLanhouse Client - Disconnected"))
        else:
            if self.iterable_timeout_id:
                source_remove(self.iterable_timeout_id)
            
            self.warn_msg.set_text('')
            self.wm_title.set_text(_("OpenLanhouse Client - Connected"))
    
    def set_ticket_suport(self, status):
        
        self.ticket_suport = status
        
        if not(status) and not(self.login_suport):
            self.set_lock_all(True)
            return
        else:
            self.set_lock_all(False)
            self.ticket_radio_item.set_sensitive(status)
        
        if not(status) and self.login_suport:
            self.login_radio_item.set_active(True)
        elif status and not(self.login_suport):
            self.ticket_radio_item.set_active(True)
    
    def set_login_suport(self, status):
        self.login_suport = status
        self.login_radio_item.set_sensitive(status)
        
        if not(status) and not(self.ticket_suport):
            self.set_lock_all(True)
            return
        elif not(status) and self.ticket_suport:
            self.set_lock_all(False)
            self.login_radio_item.set_active(status)
            self.ticket_radio_item.set_active(True)
        elif status and not(self.ticket_suport):
            self.set_lock_all(False)
            self.login_radio_item.set_active(status)
            self.ticket_radio_item.set_sensitive(False)
        else:
            self.set_lock_all(False)
            self.login_radio_item.set_active(status)
    
    def on_login_radio_item_toggled(self, obj):
        if not obj.get_active():
            return
        
        self.set_current(LOGIN_USER)
        
    def on_ticket_radio_item_toggled(self, obj):
        if not obj.get_active():
            return
        
        self.set_current(LOGIN_TICKET)
    
    def on_admin_radio_item_toggled(self, obj):
        if not obj.get_active():
            return
        
        print "admin"
