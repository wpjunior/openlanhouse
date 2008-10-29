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

import dbus
import dbus.service

from OpenlhClient.globals import *
_ = gettext.gettext

# Set up DBus event loop
try:
    # dbus-python 0.80 and later
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
except ImportError:
    # dbus-python prior to 0.80
    import dbus.glib

class DbusManager(dbus.service.Object):
    """ DBus Service """

    def __init__(self, client):
        self.__client = client
        # Start DBus support
        self.__session_bus = dbus.SessionBus()
        self.__bus_name = dbus.service.BusName(DBUS_INTERFACE,
                                               bus=self.__session_bus)

        dbus.service.Object.__init__(self, self.__bus_name, DBUS_PATH)
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='s')
    def get_welcome_msg(self):
        msg = _("Welcome")
        
        if 'default_welcome_msg' in self.__client.informations:
            if self.__client.informations['default_welcome_msg']:
                return msg
        
        if 'welcome_msg' in self.__client.informations:
            msg = self.__client.informations['welcome_msg']
        
        return msg
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='s')
    def get_host_name(self):
        return self.__client.name
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='s')
    def get_hash_id(self):
        return self.__client.hash_id
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='s')
    def get_description(self):
        return self.__client.description
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='d')
    def get_credit(self):
        credit = None
        
        if 'credit' in self.__client.other_info:
            credit = self.__client.other_info['credit']
        
        return credit
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='s')
    def get_credit_as_string(self):
        credit = ""
        
        if 'credit' in self.__client.other_info:
            credit = "%s %0.2f" % (self.__client.currency,
                                   self.__client.other_info['credit'])
        
        return credit
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='d')
    def get_total_to_pay(self):
        total_to_pay = None
        
        if 'total_to_pay' in self.__client.other_info:
            total_to_pay = self.__client.other_info['total_to_pay']
        
        return total_to_pay
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='s')
    def get_total_to_pay_as_string(self):
        total_to_pay = None
        
        if 'total_to_pay' in self.__client.other_info:
            total_to_pay = "%s %0.2f" % (self.__client.currency,
                            self.__client.other_info['total_to_pay'])
        
        return total_to_pay
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='s')
    def get_user_full_name(self):
        full_name = ""
        
        if 'full_name' in self.__client.other_info:
            full_name = self.__client.other_info['full_name']
        
        return full_name
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='ai')
    def get_time(self):
        return self.__client.time
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='i')
    def is_blocked(self):
        return int(self.__client.blocked)
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='i')
    def is_limited(self):
        return int(self.__client.limited)
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='i')
    def is_registred(self):
        return int(self.__client.registred)
    
    #Signals
    
    @dbus.service.method(DBUS_INTERFACE, out_signature='s')
    def get_currency(self):
        return self.__client.currency
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE,
                         signature='s')
    def welcome_msg_changed(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE,
                         signature='s')
    def host_name_changed(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE,
                         signature='s')
    def description_changed(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE,
                         signature='s')
    def currency_changed(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE,
                         signature='d')
    def credit_changed(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE,
                         signature='s')
    def credit_changed_as_string(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE,
                         signature='d')
    def total_to_pay_changed(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE,
                         signature='s')
    def total_to_pay_changed_as_string(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE,
                         signature='s')
    def full_name_changed(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE,
                         signature='ai')
    def time_changed(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE,
                         signature='u')
    def elapsed_time_changed(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE,
                         signature='u')
    def left_time_changed(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE, signature='ai')
    def unblock(self, value):
        pass
    
    @dbus.service.signal(dbus_interface=DBUS_INTERFACE)
    def block(self):
        pass
    
