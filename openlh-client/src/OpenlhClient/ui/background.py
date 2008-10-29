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
import gobject
import time

class Background(gobject.GObject):
    
    selected_window = None
    visible = False
    io_monitory_id = 0
    background_file = None
    
    def __init__(self, screen=gtk.gdk.screen_get_default()):
        
        self.background = {}
        self.background['screen'] = screen
        self.background['screen'].connect('size-changed', self.size_changed)
        self.background['area.width'] = screen.get_width()
        self.background['area.height'] = screen.get_height()
        self.background['composited'] = screen.is_composited()
        self.background['root_window'] = screen.get_root_window()
    
        self.attr = {}
        self.attr['parent'] = self.background['root_window']
        self.attr['width'] = screen.get_width()
        self.attr['height'] = screen.get_height()
        self.attr['colormap'] = screen.get_default_colormap()
        self.attr['wclass'] = gtk.gdk.INPUT_OUTPUT
        self.attr['visual'] = screen.get_system_visual()
        self.attr['window_type'] = gtk.gdk.WINDOW_CHILD
        self.attr['override_redirect'] = True
    
        self.attr['event_mask'] = (gtk.gdk.WA_X | gtk.gdk.WA_Y |
                gtk.gdk.WA_VISUAL | gtk.gdk.WA_COLORMAP | gtk.gdk.WA_NOREDIR)
    
        self.background['draw_window'] = gtk.gdk.Window(**self.attr)
        self.window = self.background['draw_window']
        
        self.windows = []
        self.grabed_window = None
        
        self._pointer_events = (gtk.gdk.POINTER_MOTION_MASK |
                gtk.gdk.POINTER_MOTION_HINT_MASK | gtk.gdk.BUTTON_PRESS_MASK |
                                                  gtk.gdk.BUTTON_RELEASE_MASK)
        
        self.start_monitory()
    
    def show(self):
        self.visible = True
        self.background['draw_window'].show()
    
    def hide(self):
        self.visible = False
        self.background['draw_window'].hide()
    
    def set_background(self, image):
        self.background_file = image
        if not image:
            self.window.set_background(gtk.gdk.color_parse("black"))
            self.window.clear()
            gtk.gdk.flush()
            return
        
        pb = gtk.gdk.pixbuf_new_from_file(image).scale_simple(
                             gtk.gdk.screen_width(),
                             gtk.gdk.screen_height(),
                             gtk.gdk.INTERP_BILINEAR)
        
        width, height = self.window.get_size()
        pm = gtk.gdk.Pixmap(self.window, width, height)
        
        if not pm:
            return
        
        pm.draw_pixbuf(None, pb, 0, 0, 0, 0, -1, -1,
                       gtk.gdk.RGB_DITHER_MAX, 0, 0)
        
        self.window.set_back_pixmap(pm, False)
        self.window.clear()
        
        gtk.gdk.flush()

    def _set_left_cursor(self, window):
        window = self._get_gdk_window(window)
        window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
    
    def _get_gdk_window(self, window):
        if isinstance(window, gtk.Window):
            window.realize()
            window = window.window
        
        return window
    
    def _lock_keyboard(self, window):
        window = self._get_gdk_window(window)
        status = gtk.gdk.keyboard_grab(window, True)
        gtk.gdk.flush()
        
        return status
    
    def _lock_pointer(self, window):
        window = self._get_gdk_window(window)
        status = gtk.gdk.pointer_grab(window, True, 
                             event_mask = self._pointer_events)
        
        gtk.gdk.flush()
        
        return status
    
    def _grab(self, window):
        window.show()
        self.grabed_window = window
        self._set_left_cursor(window)
        window.set_keep_below(True)
        pstatus = self._lock_pointer(window)
        kstatus = self._lock_keyboard(window)
        window.set_keep_above(True)
        
    def _ungrab(self, window):
        self.grabed_window = None
        window.set_keep_above(False)
        gtk.gdk.pointer_ungrab()
        gtk.gdk.keyboard_ungrab()
        
    def set_window(self, idx):
        self.selected_window = idx
        if idx <= len(self.windows):
            if self.grabed_window:
                self._ungrab(self.windows[idx])
            self._grab(self.windows[idx])
    
    def add_window(self, window):
        if not window in self.windows:
            self.windows.append(window)
        
        return self.windows.index(window)
    
    def del_window(self, window):
        self.windows.remove(window)
    
    def get_windows(self):
        return self.windows
        
    def start_monitory(self):
        if self.grabed_window and not(gtk.gdk.pointer_is_grabbed()):
            self._lock_pointer(self.grabed_window)
            self._lock_keyboard(self.grabed_window)
        
        self.io_monitory_id = gobject.timeout_add(500, self.start_monitory)
    
    def stop_monitory(self):
        if self.io_monitory_id:
            gobject.source_remove(self.io_monitory_id)
    
    def size_changed(self, obj):
        self.set_background(self.background_file)
        self.background['area.width'] = gtk.gdk.screen_width()
        self.background['area.height'] = gtk.gdk.screen_height()
        
        self.background['draw_window'].resize(gtk.gdk.screen_width(),
                                              gtk.gdk.screen_height())
        
