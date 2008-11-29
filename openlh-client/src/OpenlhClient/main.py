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
import time
import logging
import gtk
import gobject

from OpenlhCore.net.client import NetClient
from OpenlhCore.ConfigClient import get_default_client

from OpenlhClient.ui import icons
from OpenlhClient.ui import tray
from OpenlhClient.globals import *
from OpenlhCore.utils import md5_cripto, kill_process
from OpenlhCore.utils import get_os, humanize_time
from OpenlhClient.ui import dialogs, login
from OpenlhClient.ui.utils import get_gtk_builder
from OpenlhClient.logout_actions import ActionManager


try:
    from OpenlhClient.dbus_manager import DbusManager
except ImportError:
    
    def gambiarra_caller(*args):
        pass
    
    #gambiarra
    class DbusManager:
        def __init__(self, *args, **kwargs):
            pass
        
        def __getattr__(self, *args):
            return gambiarra_caller
        
        def __setattr__(self, *args):
            pass

from os import remove
from os import path as ospath
_ = gettext.gettext

class Client:
    
    name = None
    description = None
    locked = False
    informations = {}
    other_info = {}
    logo_md5 = None
    background_md5 = None
    visible = False
    monitory_handler_id = 0
    update_time_handler_id = 0
    cleanup_apps_id = 0
    cleanup_apps_timeout = 30
    currency = "US$" #by default
    interative = True
    login_attempts = 0
    blocked = True
    
    limited = False
    registred = False
    os_name = ""
    os_version = ""
    
    def __init__(self):
        
        self.logger = logging.getLogger('client.main')
        self.conf_client = get_default_client()
        self.dbus_manager = DbusManager(self)
        
        # Get operating system version
        o = get_os()
        if o[0]:
            self.os_name = o[0]
        if o[1]:
            self.os_version = o[1]
        
        #BACKGROUND MD5SUM
        if ospath.exists(BACKGROUND_CACHE):
            try:
                assert ospath.getsize(BACKGROUND_CACHE) < 2500000L, "Large Background"
                self.background_md5 = md5_cripto(open(BACKGROUND_CACHE).read())
            except Exception, error:
                self.logger.error(error)
                self.background_md5 = None
        
        if self.background_md5:
            self.logger.info("Background Md5sum is %s" % self.background_md5)
        
        #LOGO MD5SUM
        if ospath.exists(LOGO_CACHE):
            try:
                assert ospath.getsize(LOGO_CACHE) < 2500000L, "Large Logo"
                self.logo_md5 = md5_cripto(open(LOGO_CACHE).read())
            except Exception, error:
                self.logger.error(error)
                self.logo_md5 = None
        
        if self.logo_md5:
            self.logger.info("Logo Md5sum is %s" % self.logo_md5)
        
        self.hash_id = self.conf_client.get_string('hash_id')
        self.server = self.conf_client.get_string('server')
        self.port = self.conf_client.get_int('port')
        
        if not self.port:
            self.port = 4558
        
        self.netclient = NetClient(self.server, self.port,
                            CLIENT_TLS_CERT, CLIENT_TLS_KEY, self.hash_id)
        
        self.netclient.connect('connected', self.connected)
        self.netclient.connect('disconnected', self.disconnected)
        self.netclient.dispatch_func = self.dispatch
        self.netclient.recvfile_func = self.recvfile_func
        
        #icons
        self.icons = icons.Icons()
        self.logo = self.icons.get_icon(CLIENT_ICON_NAME)
        
        #MainWindow
        self.xml = get_gtk_builder('main')
        self.main_window = self.xml.get_object('window')
        self.time_str = self.xml.get_object('time_str')
        self.elapsed_pb = self.xml.get_object('elapsed_pb')
        self.remaining_pb = self.xml.get_object('remaining_pb')
        self.full_name = self.xml.get_object('full_name')
        self.credit = self.xml.get_object('credit')
        self.total_to_pay = self.xml.get_object('total_to_pay')
        self.tray_menu = self.xml.get_object('tray_menu')
        self.show_window_menu = self.xml.get_object('show_window_menu')
        
        if self.conf_client.get_bool('ui/visible'):
            self.main_window.show()
            self.visible = True
            self.show_window_menu.set_active(True)
        
        b = self.conf_client.get_bool('ui/show_informations')
        self.show_informations(b)
        
        b = self.conf_client.get_bool('ui/show_time_elapsed')
        self.show_time_elapsed(b)
        
        b = self.conf_client.get_bool('ui/show_time_remaining')
        self.show_time_remaining(b)
        
        self.xml.connect_signals(self)
        
        #Tray
        self.tray = tray.Tray(_("OpenLanhouse - Client"), None, "openlh-client")
        
        if self.tray.iconsuport:
            self.tray.icon.connect('popup-menu', self.on_tray_popup_menu)
            self.tray.icon.connect('activate', self.on_show_hide)
        
        #Login Window
        self.login_window = login.Login(self)
        self.login_window.run()
        
        if not self.netclient.start():
            self.login_window.set_connected(False)
    
    def on_window_delete_event(self, *args):
        self.on_show_hide(None)
        return True
    
    def on_show_hide(self, obj):
        
        if obj == self.show_window_menu:
            if self.visible != obj.get_active():
                if self.visible:
                    self.visible = False
                    self.main_window.hide()
                else:
                    self.visible = True
                    self.main_window.show()
                
                self.conf_client.set_bool('ui/visible',
                                           self.visible)
        else:
            if self.visible:
                self.visible = False
                self.show_window_menu.set_active(False)
                self.main_window.hide()
            else:
                self.visible = True
                self.show_window_menu.set_active(True)
                self.main_window.show()
            
            self.conf_client.set_bool('ui/visible',
                                       self.visible)
    
    def on_tray_popup_menu(self, obj, button, event):
        self.tray_menu.popup(None, None, None, button, event)
    
    def on_about_menuitem_activate(self, obj):
        dialogs.about(self.logo, self.main_window)
    
    def send_myos(self):
        self.netclient.request("set_myos", (self.os_name, self.os_version))
        
    def connected(self, obj, server):
        self.login_window.set_connected(True)
        gobject.timeout_add(10000,
                            self.send_myos)
        
    def disconnected(self, obj):
        self.block(False, 0)
        self.login_window.set_connected(False)
        
    def set_myinfo(self, data):
        if data.has_key('name'):
            self.name = data['name']
            self.dbus_manager.host_name_changed(self.name)
            
            if 'welcome_msg' in self.informations:
                self.login_window.set_title(
                    self.informations['welcome_msg'].replace("%n", self.name)
                    )
            
            self.logger.debug('My host name is "%s"' % data['name'])
            
        
        if data.has_key('description'):
            self.description = data['description']
            self.dbus_manager.description_changed(self.description)
            self.logger.debug('My host description is "%s"' % data['description'])
    
    def set_background(self, string_buffer):
        self.logger.debug('Setting up new background')
        
        if ospath.exists(BACKGROUND_CACHE):
            remove(BACKGROUND_CACHE)
            
        open(BACKGROUND_CACHE, 'w').write(string_buffer)
        
        try:
            assert ospath.getsize(BACKGROUND_CACHE) < 2500000L, "Large Background"
            self.background_md5 = md5_cripto(open(BACKGROUND_CACHE).read())
        except Exception, error:
            self.logger.error(error)
            self.background_md5 = None
            return
        
        if self.background_md5:
            self.logger.info("Background Md5sum is %s" % self.background_md5)
        
        if ('use_background' in self.informations 
                    and self.informations['use_background']):
            self.login_window.set_background(BACKGROUND_CACHE)
        else:
            self.login_window.set_background(None)
        
    def set_logo(self, string_buffer):
        self.logger.debug('Setting up new logo')
        
        if ospath.exists(LOGO_CACHE):
            remove(LOGO_CACHE)
        
        open(LOGO_CACHE, 'w').write(string_buffer)
        
        try:
            assert ospath.getsize(LOGO_CACHE) < 2500000L, "Large Background"
            self.logo_md5 = md5_cripto(open(LOGO_CACHE).read())
        except Exception, error:
            self.logger.error(error)
            self.logo_md5 = None
            return
        
        if self.logo_md5:
            self.logger.info("Logo Md5sum is %s" % self.logo_md5)
        
        if ('use_logo' in self.informations 
                    and self.informations['use_logo']):
            self.login_window.set_logo(LOGO_CACHE)
        else:
            self.login_window.set_logo(None)
    
    def set_information(self, data):
        assert isinstance(data, dict)
        
        for key in data:
            self.informations[key] = data[key]
        
        if 'ticket_suport' in data:
            self.login_window.set_ticket_suport(self.informations['ticket_suport'])
        
        if 'login_suport' in data:
            self.login_window.set_login_suport(self.informations['login_suport'])
        
        if 'ticket_size' in data:
            self.login_window.max_ticket_size = data['ticket_size']
        
        if 'welcome_msg' in data:
            self.login_window.set_title(
                    self.informations['welcome_msg'].replace("%n", self.name)
                    )
            self.dbus_manager.welcome_msg_changed(self.informations['welcome_msg'])
        
        if 'default_welcome_msg' in data:
            if data['default_welcome_msg']:
                self.login_window.set_title(_('Welcome'))
                self.dbus_manager.welcome_msg_changed(_('Welcome'))
            else:
                self.login_window.set_title(
                       self.informations['welcome_msg'].replace("%n", self.name)
                       )
                self.dbus_manager.welcome_msg_changed(self.informations['welcome_msg'])
        
        if 'currency' in data:
            self.currency = data['currency']
            self.dbus_manager.currency_changed(self.currency)
        
        background_requested = False
        if 'background_md5' in data:
            if (data['background_md5'] != self.background_md5 
                                    or not(self.background_md5)):
                self.netclient.request('get_background')
                background_requested = True
        
        logo_requested = False
        if 'logo_md5' in data:
            if (data['logo_md5'] != self.logo_md5 or not(self.logo_md5)):
                self.netclient.request('get_logo')
                logo_requested = True
        
        if 'use_background' in data:
            if data['use_background'] and not(background_requested):
                self.login_window.set_background(BACKGROUND_CACHE)
            else:
                self.login_window.set_background(None)
        
        if 'use_logo' in data:
            if data['use_logo'] and not(logo_requested):
                self.login_window.set_logo(LOGO_CACHE)
            else:
                self.login_window.set_logo(None)
        
    def reset_widgets(self):
        self.credit.set_text("")
        self.full_name.set_text("")
        self.total_to_pay.set_text("")
        self.elapsed_pb.set_text("")
        self.elapsed_pb.set_fraction(0.0)
        self.remaining_pb.set_text("")
        self.remaining_pb.set_fraction(0.0)
        self.other_info = {}
    
    def do_cleanup_timeout(self):
        self.cleanup_apps_timeout -= 1
        
        if self.cleanup_apps_timeout == 0:
            if self.login_window.iterable_timeout_id == 0: #check
                self.login_window.set_warn_message("")
            
            if 'close_apps_list' in self.informations:
                for a in self.informations['close_apps_list']:
                    kill_process(a) # Kill process
                    
            self.cleanup_apps_id = 0
            return
        
        if self.login_window.iterable_timeout_id == 0: #check
            self.login_window.set_warn_message(
                _("Closing applications in %0.2d seconds") % (self.cleanup_apps_timeout + 1))
        
        self.cleanup_apps_id = gobject.timeout_add_seconds(1,
                                                           self.do_cleanup_timeout)

    def block(self, after, action, cleanup_apps=True):
        self.blocked = True
        self.elapsed_time = 0
        self.left_time = 0
        self.limited = False
        self.registred = False
        self.update_time = None
        self.time = (0, 0)
        self.reset_widgets()
        
        self.login_window.lock()
        self.stop_monitory_status()
        self.dbus_manager.block()
        
        if 'close_apps' in self.informations:
            if self.informations['close_apps'] and cleanup_apps:
                self.cleanup_apps_timeout = 30
                self.do_cleanup_timeout()
        
        if not ActionManager:
            return

        if not after:
            return

        if action == 0 : #shutdown
            ActionManager.shutdown()
            
        elif action == 1: #reboot
            ActionManager.reboot()
            
        elif action == 2: #logout
            ActionManager.logout()
    
    def unblock(self, data):
        assert isinstance(data, dict)
        
        self.blocked = False
        self.reset_widgets()
        self.elapsed_time = 0
        self.left_time = 0
        self.update_time = None
        self.time = (0, 0)
        
        if self.cleanup_apps_id > 0:
            gobject.source_remove(self.cleanup_apps_id)
            self.cleanup_apps_id = 0

        if 'limited' in data and 'registred' in data:
            self.limited = data['limited']
            self.registred = data['registred']
            
            self.dbus_manager.unblock((int(data['registred']), 
                                       int(data['limited'])))
        
        if 'time' in data:
            self.time = data['time']
            self.dbus_manager.time_changed(data['time'])
        
        if 'registred' in data:
            if data['registred']:
                self.xml.get_object("information_vbox").show()
                self.xml.get_object("information_menuitem").set_sensitive(True)
            else:
                self.xml.get_object("information_vbox").hide()
                self.xml.get_object("information_menuitem").set_sensitive(False)
        
        if 'limited' in data:
            self.xml.get_object("remaining_label").set_property('visible', bool(data['limited']))
            self.xml.get_object("remaining_pb").set_property('visible', bool(data['limited']))
            self.xml.get_object("time_remaining_menuitem").set_property('sensitive', bool(data['limited']))
        
        self.start_monitory_status()
        self.login_window.unlock(None)
    
    def dispatch(self, method, params):
        
        if method == 'core.get_hash_id':
            return self.hash_id
            
        elif method == 'main.set_myinfo':
            self.set_myinfo(*params)
            return True
        
        elif method == 'core.set_information':
            self.set_information(*params)
            return True
        
        elif method == 'core.unblock':
            self.unblock(*params)
            return True
        
        elif method == 'core.block':
            self.block(*params)
            return True
        
        elif method == 'set_status':
            self.set_status(*params)
            return True
        
        elif method == 'system.shutdown':
            self.system_shutdown()
            return True
            
        elif method == 'system.reboot':
            self.system_reboot()
            return True
        
        elif method == 'system.logout':
            self.system_logout()
            return True
        
        elif method == 'app.quit':
            self.app_quit()
            return True
        
        else:
            print method, params
            return True
    
    def recvfile_func(self, method, data):
        if method == 'main.set_background':
            self.set_background(data)
            
        elif method == 'main.set_logo':
            self.set_logo(data)
    
    def reload_network(self):
        self.netclient = NetClient(self.server, self.port,
                            CLIENT_TLS_CERT, CLIENT_TLS_KEY, self.hash_id)
        
        self.netclient.connect('connected', self.connected)
        self.netclient.connect('disconnected', self.disconnected)
        self.netclient.dispatch_func = self.dispatch
        self.netclient.recvfile_func = self.recvfile_func
        
    def update_time_status(self):
        if not self.update_time:
            self.update_time_handler_id = gobject.timeout_add(1000, 
                                                self.update_time_status)
            return
        
        now = int(time.time())
        diff_secs = now - self.update_time
        melapsed_time = self.elapsed_time + diff_secs
        self.dbus_manager.elapsed_time_changed(melapsed_time)
        time_elapsed_str = "%0.2d:%0.2d:%0.2d" % humanize_time(melapsed_time)
        
        if self.limited:
            mleft_time = self.left_time - diff_secs
            self.dbus_manager.left_time_changed(mleft_time)
            time_left_str = "%0.2d:%0.2d:%0.2d" % humanize_time(mleft_time)
            time_left_per = float(mleft_time) / float(self.mtime)
            time_elapsed_per = float(melapsed_time) / float(self.mtime)
        else:
            time_left_str = _("None")
            time_left_per = 0
            time_elapsed_per = 0
        
        self.elapsed_pb.set_text(time_elapsed_str)
        self.elapsed_pb.set_fraction(time_elapsed_per)
        self.remaining_pb.set_text(time_left_str)
        self.remaining_pb.set_fraction(time_left_per)
        
        self.update_time_handler_id = gobject.timeout_add(1000,
                                        self.update_time_status)
    
    def monitory_status(self):
        request = self.netclient.request('get_status')
        request.connect("done", self.on_get_status_request_done)
        self.monitory_handler_id = gobject.timeout_add(120000,
                                        self.monitory_status)
        
    def start_monitory_status(self):
        self.update_time_status()
        self.monitory_status()
    
    def stop_monitory_status(self):
        if self.monitory_handler_id:
            gobject.source_remove(self.monitory_handler_id)
        if self.update_time_handler_id:
            gobject.source_remove(self.update_time_handler_id)
    
    def set_status(self, data):
        for key in data:
            self.other_info[key] = data[key]
        
        if 'credit' in data:
            self.credit.set_text(
                    "%s %0.2f" % (self.currency, data['credit']))
            self.dbus_manager.credit_changed(data['credit'])
            self.dbus_manager.credit_changed_as_string("%s %0.2f" % 
                                        (self.currency, data['credit']))
        
        if 'full_name' in data:
            self.full_name.set_text(data['full_name'])
            self.dbus_manager.full_name_changed(data['full_name'])
        
        if 'total_to_pay' in data:
            ats = "%s %0.2f" % (self.currency, data['total_to_pay'])
            self.total_to_pay.set_text(ats)
            self.dbus_manager.total_to_pay_changed(data['total_to_pay'])
            self.dbus_manager.total_to_pay_changed_as_string(ats)
        
        if 'time' in data and 'left_time' in data and 'elapsed' in data:
            self.update_time = int(time.time())
        
        if 'time' in data:
            assert len(data['time']) == 2
            assert self.limited
            self.time = data['time']
            self.mtime = ((self.time[0] * 3600) + self.time[1] * 60)
            time_str = "%0.2d:%0.2d" % tuple(self.time)
            self.time_str.set_text(time_str)
            self.dbus_manager.time_changed(self.time)
        
        if 'left_time' in data:
            assert self.limited
            self.left_time = data['left_time']
        
        if 'elapsed' in data:
            self.elapsed_time = data['elapsed']
        
    def on_get_status_request_done(self, request, value):
        self.update_time = int(time.time())
        self.limited = value['limited']
        self.elapsed_time = value['elapsed']
        
        if self.limited:
            self.left_time = value['left_time']
            self.time = value['time']
            self.mtime = ((self.time[0] * 3600) + self.time[1] * 60)
            
            assert len(value['time']) == 2
            time_str = "%0.2d:%0.2d" % tuple(self.time)
        else:
            self.left_time = None
            self.time = None
            self.mtime = None
            time_str = _("Unlimited")
        
        self.time_str.set_text(time_str)
    
    def show_informations(self, status):
        self.interative = False
        self.xml.get_object("information_vbox").set_property('visible', status)
        self.conf_client.set_bool('ui/show_informations',
                                   status)
        self.xml.get_object("information_menuitem").set_active(status)
        self.interative = True
    
    def show_time_elapsed(self, status):
        self.interative = False
        self.xml.get_object("elapsed_label").set_property('visible', status)
        self.xml.get_object("elapsed_pb").set_property('visible', status)
        self.conf_client.set_bool('ui/show_time_elapsed',
                                   status)
        self.xml.get_object("time_elapsed_menuitem").set_active(status)
        self.interative = True
    
    def show_time_remaining(self, status):
        self.interative = False
        self.xml.get_object("remaining_label").set_property('visible', status)
        self.xml.get_object("remaining_pb").set_property('visible', status)
        self.conf_client.set_bool('ui/show_time_remaining',
                                   status)
        self.xml.get_object("time_remaining_menuitem").set_active(status)
        self.interative = True
    
    def on_information_toggled(self, obj):
        if self.interative:
            self.show_informations(obj.get_active())
        
    def on_time_elapsed_toggled(self, obj):
        if self.interative:
            self.show_time_elapsed(obj.get_active())
    
    def on_time_remaining_toggled(self, obj):
        if self.interative:
            self.show_time_remaining(obj.get_active())
    
    def on_login_response(self, obj, value):
        self.login_window.set_lock_all(False)
        
        if value==True:
            self.login_attempts = 0
        elif value==False:
            self.login_attempts += 1
            self.login_window.err_box.set_text(
                            _("Incorrect username or password."))
        elif value==2:
            self.login_attempts = 0
            self.login_window.err_box.set_text(
                            _("Insufficient Credits."))
        
        elif value==3:
            self.login_attempts = 0
            self.login_window.err_box.set_text(
                            _("Permission Denied"))
        
        if self.login_attempts >= 3:
            self.login_window.set_lock_all(True)
            self.login_window.on_ready_run_interable = True
            self.login_window.on_ready = 60
            
            if self.login_window.iterable_timeout_id:
                gobject.source_remove(self.login_window.iterable_timeout_id)
            
            self.login_window.on_ready_iterable()
            
        self.login_window.set_current(login.LOGIN_USER)
        
    def on_ticket_response(self, obj, value):
        self.login_window.set_lock_all(False)
        
        if value==True:
            self.login_attempts = 0
        elif value==False:
            self.login_attempts += 1
            self.login_window.err_box.set_text(
                            _("Ticket Invalid."))
                
        if self.login_attempts >= 3:
            self.login_window.set_lock_all(True)
            self.login_window.on_ready_run_interable = True
            self.login_window.on_ready = 60
            
            if self.login_window.iterable_timeout_id:
                gobject.source_remove(self.login_window.iterable_timeout_id)
            
            self.login_window.on_ready_iterable()
            
        self.login_window.set_current(login.LOGIN_TICKET)
        
    def on_login(self, username, password):
        self.login_window.set_lock_all(True)
        request = self.netclient.request('login', (username, password))
        request.connect("done", self.on_login_response)
        
    def on_ticket(self, ticket):
        self.login_window.set_lock_all(True)
        request = self.netclient.request('send_ticket', ticket)
        request.connect('done', self.on_ticket_response)
    
    def on_logout_menuitem_activate(self, obj):
        dlg = gtk.MessageDialog(parent=self.main_window,
                                type=gtk.MESSAGE_QUESTION,
                                buttons=gtk.BUTTONS_YES_NO)
        
        dlg.set_markup(_("<big><b>Are you sure you want to Log out "
                         "of this system now?</b></big>\n\n"
                         "If you Log out, unsaved work will be lost."))
        response = dlg.run()
        dlg.destroy()
        
        if response == gtk.RESPONSE_YES:
            self.netclient.request('logout')
            

    def system_shutdown(self):
        if not ActionManager:
            return
        
        ActionManager.shutdown()

    def system_reboot(self):
        if not ActionManager:
            return
        
        ActionManager.reboot()

    def system_logout(self):
        if not ActionManager:
            return
        
        ActionManager.logout()

    def app_quit(self):
        gtk.main_quit()                
