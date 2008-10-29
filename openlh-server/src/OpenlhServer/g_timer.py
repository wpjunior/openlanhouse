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

import gobject
import time
import gtk

class TimeredObj(gobject.GObject):
    
    elapsed_time = 0
    
    __gsignals__ = {'done':(gobject.SIGNAL_RUN_FIRST,
                                     gobject.TYPE_NONE,
                                     ()),
                    }
    
    def __init__(self, name=None):
        self._name = name
        self.__gobject_init__()
        self._stop_time = None
        self._start_time = time.time()
        
    def reset_start_time(self):
        self._start_time = time.time()
        self._stop_time = None

    def set_stop_time(self, stop_time):
        self._stop_time = stop_time

gobject.type_register(TimeredObj)

class TimerManager(gobject.GObject):
    
    timered_objs = []
    active_timered_objs = []
    done_timered_objs = []
    io_handler_id = 0

    def __init__(self):
       self.__gobject_init__()

    def add_timerd_obj(self, obj):
        if not isinstance(obj, TimeredObj):
            raise TypeError, "obj must be TimeredObj Object"
        
        else:
            self.timered_objs.append(obj)
            self.active_timered_objs.append(obj)
    
    def get_timerd_objs(self):
        return tuple(self.timered_objs)

    def remove_timered_obj(self, obj):
        if obj in self.timered_objs:
            self.timered_objs.remove(obj)
        if obj in self.active_timered_objs:
            self.active_timered_objs.remove(obj)
        if obj in self.done_timered_objs:
            self.done_timered_objs.remove(obj)

        obj.elapsed_time = 0

    def handle_events(self):
        for obj in self.active_timered_objs:
            current_time = time.time()
            obj.elapsed_time = int(current_time - obj._start_time)
            
            if obj._stop_time:
                if obj.elapsed_time >= obj._stop_time:
                    self.active_timered_objs.remove(obj)
                    self.done_timered_objs.append(obj)
                    obj.emit("done")
        
        self.io_handler_id = gobject.timeout_add(1000, self.handle_events)
        
    def run(self):
        self.io_handler_id = gobject.timeout_add(1000, self.handle_events)
    
    def stop(self):
        if self.io_handler_id:
            gobject.source_remove(self.io_handler_id)

gobject.type_register(TimerManager)
