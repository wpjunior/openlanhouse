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

from gtk import HBox, SpinButton, Label, UPDATE_IF_VALID
from gobject import type_register, TYPE_PYOBJECT, PARAM_READWRITE, SIGNAL_RUN_LAST, TYPE_NONE

class HourEntry(HBox):
    __gtype_name__ = 'HourEntry'
    
    __gproperties__ = {
        'hour' : (TYPE_PYOBJECT, 'Hour', 'The hour currently selected', PARAM_READWRITE),
        'minute' : (TYPE_PYOBJECT, 'Minute', 'The minute currently selected', PARAM_READWRITE),
        'second' : (TYPE_PYOBJECT, 'Second', 'The second currently selected', PARAM_READWRITE),
    }
    
    __gsignals__ = {
        'time_changed' : (SIGNAL_RUN_LAST, TYPE_NONE, ()),
    }
    
    hour = 00
    minute = 00
    second = 00
    lock = False
    
    def __init__(self):
        HBox.__init__(self)
        self.set_spacing(3)
        
        #hour spin
        self.__hour_spin = SpinButton()
        self.__hour_spin.set_range(00, 99)
        self.__hour_spin.set_width_chars(2)
        self.__hour_spin.set_increments(1, 1)
        self.__hour_spin.set_numeric(True)
        self.__hour_spin.set_update_policy(UPDATE_IF_VALID)
        self.__hour_spin.set_snap_to_ticks(True)
        self.__hour_spin.connect("output", self._on_spin_output)
        self.__hour_spin_handler = (self.__hour_spin.connect("value-changed",
                                  self.hour_spin_changed))
        self.pack_start(self.__hour_spin)
        self.__hour_spin.show()
        
        #separator
        sep = Label(":")
        self.pack_start(sep, expand=False)
        sep.show()
        
        #minute spin
        self.__minute_spin = SpinButton()
        self.__minute_spin.set_range(00, 59)
        self.__minute_spin.set_width_chars(2)
        self.__minute_spin.set_increments(1, 1)
        self.__minute_spin.set_numeric(True)
        self.__minute_spin.set_wrap(True)
        self.__minute_spin.set_update_policy(UPDATE_IF_VALID)
        self.__minute_spin.set_snap_to_ticks(True)
        self.__minute_spin.connect("output", self._on_spin_output)
        self.__minute_spin.connect("wrapped", self._on_minute_wrap)
        self.__minute_spin_handler = (self.__minute_spin.connect("value-changed",
                                  self.minute_spin_changed))
        self.pack_start(self.__minute_spin)
        self.__minute_spin.show()
        
        #separator
        self.__second_sep = Label(":")
        self.pack_start(self.__second_sep, expand=False)
        self.__second_sep.show()
        
        #seconds spin
        self.__second_spin = SpinButton()
        self.__second_spin.set_range(00, 59)
        self.__second_spin.set_width_chars(2)
        self.__second_spin.set_increments(1, 1)
        self.__second_spin.set_numeric(True)
        self.__second_spin.set_wrap(True)
        self.__second_spin.set_update_policy(UPDATE_IF_VALID)
        self.__second_spin.set_snap_to_ticks(True)
        self.__second_spin.connect("output", self._on_spin_output)
        self.__second_spin.connect("wrapped", self._on_second_wrap)
        self.__second_spin_handler = (self.__second_spin.connect("value-changed",
                                      self.second_spin_changed))
        self.pack_start(self.__second_spin)
        self.__second_spin.show()
        
    def set_hour(self, hour):
        self.__hour_spin.set_value(hour)
        self.hour = int(self.__hour_spin.get_value())
        
    def set_minute(self, minute):
        self.__minute_spin.set_value(minute)
        self.minute = int(self.__minute_spin.get_value())
    
    def set_second(self, second):
        self.__second_spin.set_value(second)
        self.second = int(self.__second_spin.get_value())
    
    def set_time(self, hour, minute, second):
        
        self.__hour_spin.handler_block(self.__hour_spin_handler)
        self.__minute_spin.handler_block(self.__minute_spin_handler)
        self.__second_spin.handler_block(self.__second_spin_handler)
        
        self.__hour_spin.set_value(hour)
        self.hour = int(self.__hour_spin.get_value())
        
        self.__minute_spin.set_value(minute)
        self.minute = int(self.__minute_spin.get_value())
        
        self.__second_spin.set_value(second)
        self.second = int(self.__second_spin.get_value())
        
        self.__hour_spin.handler_unblock(self.__hour_spin_handler)
        self.__minute_spin.handler_unblock(self.__minute_spin_handler)
        self.__second_spin.handler_unblock(self.__second_spin_handler)
        
        self.emit("time_changed")
        
    def get_time(self):
        return self.hour, self.minute, self.second
        
    # get_properties
    def do_get_property(self, property):
        
        data = {"hour":self.hour, "minute":self.minute, "second":self.second}
        
        if data.has_key(property.name):
            return data[property.name]
        else:
            raise AttributeError, 'unknown property %s' % property.name
    
    def do_set_property(self, property, value):
        if property.name == 'hour':
            self.set_hour(value)
        elif property.name == 'minute':
            self.set_minute(value)
        elif property.name == 'second':
            self.set_second(value)
        else:
            raise AttributeError, 'unknown property %s' % property.name
    
    def _on_minute_wrap(self, obj):
        self.lock = True
        if obj.get_value() == 59:
            value = self.__hour_spin.get_value_as_int() - 1
        else:
            value = self.__hour_spin.get_value_as_int() + 1
        
        self.__hour_spin.set_value(value)
        self.lock = False
        self.emit("time_changed")
    
    def _on_second_wrap(self, obj):
        self.lock = True
        minute_value = self.__minute_spin.get_value_as_int()
        second_value = obj.get_value_as_int()
        hour_value = None
        
        if minute_value == 59 and second_value == 0:
            hour_value = self.__hour_spin.get_value_as_int() + 1
        elif minute_value == 0 and second_value == 59:
            hour_value = self.__hour_spin.get_value_as_int() - 1
        
        if not(hour_value is None):
            self.__hour_spin.set_value(hour_value)
        
        if second_value == 59:
            minute_value -= 1
        elif second_value == 0:
            minute_value += 1
        
        if minute_value == 60:
            minute_value = 0
        elif minute_value == -1:
            minute_value = 59
        
        self.__minute_spin.set_value(minute_value)
        self.lock = False
        self.emit("time_changed")
    
    def _on_spin_output(self, obj):
        obj.set_text("%02d" % obj.get_adjustment().get_value())
        return True
    
    def hour_spin_changed(self, obj):
        self.hour = obj.get_value_as_int()
        
        if not self.lock:
            self.emit("time_changed")
    
    def minute_spin_changed(self, obj):
        self.minute = obj.get_value_as_int()
        
        if not self.lock:
            self.emit("time_changed")
    
    def second_spin_changed(self, obj):
        self.second = obj.get_value_as_int()
        
        if not self.lock:
            self.emit("time_changed")
    
    def set_second_visible(self, s):
        if s:
            self.__second_spin.show()
            self.__second_sep.show()
        else:
            self.__second_spin.hide()
            self.__second_sep.hide()

type_register(HourEntry)
