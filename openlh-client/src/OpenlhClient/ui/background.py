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

from os import path as ospath
from os import name as osname
import gtk
import gobject

if osname == 'nt':
    import win32gui
    import win32con
    import pyHook

class X11LockScreenWindow(gtk.Window):
    
    rc_parse_first_time = True
    background_file = None
    background_color = 'black'
    visible = False
    child_window = None
    grabed_window = None
    grab_connect_id = 0
    
    bntevents = (gtk.gdk.BUTTON_PRESS , gtk.gdk._2BUTTON_PRESS,
                 gtk.gdk._3BUTTON_PRESS, gtk.gdk.BUTTON_RELEASE)
 
    keyevents = (gtk.gdk.KEY_PRESS, gtk.gdk.KEY_RELEASE)

    
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_left_cursor(self)

        self.fullscreen()
                        
        self.vbox = gtk.VBox(spacing=12)
        self.vbox.show()
        self.add(self.vbox)
        
        self.drawing_area = gtk.DrawingArea()
        self.drawing_area.show()
        self.vbox.add(self.drawing_area)
        self.force_no_pixmap_background(self.drawing_area)
        
        # resize changed callback
        screen = gtk.gdk.screen_get_default()
        screen.connect('size-changed', self.on_size_changed)
        
    def force_no_pixmap_background(self, widget):
        if self.rc_parse_first_time:
            gtk.rc_parse_string("\n"
                                "   style \"gs-theme-engine-style\"\n"
                                "   {\n"
                                "      bg_pixmap[NORMAL] = \"<none>\"\n"
                                "      bg_pixmap[INSENSITIVE] = \"<none>\"\n"
                                "      bg_pixmap[ACTIVE] = \"<none>\"\n"
                                "      bg_pixmap[PRELIGHT] = \"<none>\"\n"
                                "      bg[NORMAL] = { 0.0, 0.0, 0.0 }\n"
                                "      bg[INSENSITIVE] = { 0.0, 0.0, 0.0 }\n"
                                "      bg[ACTIVE] = { 0.0, 0.0, 0.0 }\n"
                                "      bg[PRELIGHT] = { 0.0, 0.0, 0.0 }\n"
                                "   }\n"
                                "   widget \"gs-window-drawing-area*\" style : highest \"gs-theme-engine-style\"\n"
                                "\n")
            self.rc_parse_first_time = False
        
        widget.set_name("gs-window-drawing-area")
    
    def clear_widget(self, widget):
        color = gtk.gdk.color_parse(self.background_color)
        
        if not(widget.flags() & gtk.VISIBLE):
            return
        
        for i in range(0, len(widget.style.bg)):
            widget.style.bg[i] = color
            
        style = widget.style.copy()
        
        for i in range(0, len(widget.style.bg_pixmap)):
            widget.style.bg_pixmap[i] = None
            
        colormap = widget.window.get_colormap()
        colormap.alloc_color(color, writeable=False, best_match=True)
        
        widget.window.set_background(color)
        widget.set_style(style)
        
        widget.window.clear()
        
        gtk.gdk.flush()
                
    def fullscreen(self):
        screen = gtk.gdk.screen_get_default()
        if self.window:
            self.window.move_resize(0, 0,
                                    screen.get_width(),
                                    screen.get_height())
        
    def show(self):
        self.visible = True
        gtk.Window.show(self)
        self.fullscreen()
        
        if not self.background_file:
            self.clear_widget(self.drawing_area)
            self.clear_widget(self)
        else:
            self.set_background_image(self.background_file)
            
        if self.child_window:
            self.grab(self.child_window)
            

    def hide(self):
        self.visible = False
        gtk.Window.hide(self)
        
        if self.grabed_window:
            self.ungrab(self.grabed_window)
            
    def set_color(self, color):
        self.background_color = color
        self.background_file = None
        
        self.clear_widget(self.drawing_area)
        self.clear_widget(self)

    def on_size_changed(self, screen):
        self.fullscreen()
        
        if self.background_file:
            self.set_background_image(self.background_file)
                
    def set_background_image(self, image_path):
        
        if not ospath.exists(image_path):
            return
        
        self.background_file = image_path
        self.background_color = 'black'
        
        if not self.window:
            return #this window is not realized
                
        pb = gtk.gdk.pixbuf_new_from_file(image_path).scale_simple(
            gtk.gdk.screen_width(),
            gtk.gdk.screen_height(),
            gtk.gdk.INTERP_BILINEAR)
        
        width, height = self.window.get_size()
        
        pm = gtk.gdk.Pixmap(self.drawing_area.window, width, height)
        
        if not pm:
            return
        
        pm.draw_pixbuf(None, pb, 0, 0, 0, 0, -1, -1,
                       gtk.gdk.RGB_DITHER_MAX, 0, 0)
        
        self.drawing_area.window.set_back_pixmap(pm, False)
        self.drawing_area.window.clear()
        
        gtk.gdk.flush()
        
    def set_child_window(self, window):
        if self.grabed_window:
            self.ungrab(self.grabed_window)
            
        self.child_window = window
        
        if self.visible:
            self.grab(self.child_window)
        
    def ungrab(self, window):
        window.hide()
        self.grabed_window = None
        window.set_keep_above(False)
        gtk.gdk.pointer_ungrab()
        gtk.gdk.keyboard_ungrab()
        
        if self.grab_connect_id > 0:
            gobject.source_remove(self.grab_connect_id)
            self.grab_connect_id = 0

    def grab(self, window, att=0):
        window.show()
        self.grabed_window = window
        self.set_left_cursor(window)
        #window.set_keep_below(True)
        window.set_keep_above(True)
        pstatus = self.lock_pointer(window)
        kstatus = self.lock_keyboard(window)
        window.set_keep_above(True)
        self.grab_connect_id = window.connect("event", 
                                              self.grabed_window_event)
        
        # stop after 4 attempts
        if att >= 4:
            return

        if pstatus != gtk.gdk.GRAB_SUCCESS or kstatus != gtk.gdk.GRAB_SUCCESS:
            gobject.timeout_add_seconds(1, self.grab,
                                        window,
                                        att+1)
        
    def set_left_cursor(self, window):
        window = self.get_gdk_window(window)
        window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
        
    def get_gdk_window(self, window):
        if isinstance(window, gtk.Window):
            window.realize()
            window = window.window
        
        return window
    
    def lock_keyboard(self, window):
        window = self.get_gdk_window(window)
        status = gtk.gdk.keyboard_grab(window, True)
        gtk.gdk.flush()
        
        return status
    
    def lock_pointer(self, window):
        window = self.get_gdk_window(window)
        status = gtk.gdk.pointer_grab(window, True, 0)
        
        gtk.gdk.flush()
        
        return status
    
    def grabed_window_event(self, obj, event):
        
        if event.type == gtk.gdk.GRAB_BROKEN:
            self.grab(self.child_window)
        
        elif event.type in self.bntevents:
            event.button = 1
 
        elif event.type in self.keyevents:
            if event.hardware_keycode == 0x075:
                event.hardware_keycode = 0xFFE9

class Win32LockScreenWindow(X11LockScreenWindow):
    def __init__(self):
        X11LockScreenWindow.__init__(self)

        # create a hook manager
        self.hm = pyHook.HookManager()
        # watch for all keyboard events
        self.hm.KeyDown = self.OnKeyboardEvent
        # set the hook
        self.hm.HookKeyboard()
        # create a hook manager
        self.hm = pyHook.HookManager()
        # watch for all mouse events
        self.hm.MouseAll = self.OnMouseEvent
        # set the hook
        self.hm.HookMouse()

    def ungrab(self, window):
        window.hide()
        self.grabed_window = None
        window.set_keep_above(False)
        # Win32 Backend not suport gdk grab/ungrab
        #gtk.gdk.pointer_ungrab()
        #gtk.gdk.keyboard_ungrab()
        
        if self.grab_connect_id > 0:
            gobject.source_remove(self.grab_connect_id)
            self.grab_connect_id = 0

    def grab(self, window, att=0):
        window.show()
        self.grabed_window = window
        self.set_left_cursor(window)
        #window.set_keep_below(True)
        window.set_keep_above(True)
        # Win32 Backend not suport gdk grab/ungrab
        #pstatus = self.lock_pointer(window)
        #kstatus = self.lock_keyboard(window)
        window.set_keep_above(True)
        self.grab_connect_id = window.connect("event", 
                                              self.grabed_window_event)

    def OnKeyboardEvent(self, event):
	if event.Key and event.Key.lower() in ['lwin', 'tab', 'lmenu', 'escape']:
		return False	# block these keys
	else:
		# return True to pass the event to other handlers
		return True

    def OnMouseEvent(self, event):
        if not self.visible: #allow all windows
            return True

        a = [self.window.handle]

        if self.grabed_window and win32gui.IsChild(self.grabed_window.window.handle,
                                                   event.Window):
            return True

        if self.grabed_window:
            a.append(self.grabed_window.window.handle)

        try:
            p = win32gui.GetParent(event.Window)
        except:
            return False
        
        if self.grabed_window and win32gui.IsChild(self.grabed_window.window.handle,
                                                   p):
            return True
        
        return event.Window in a

if osname == "nt":
    LockScreenWindow = Win32LockScreenWindow
else:
    LockScreenWindow = X11LockScreenWindow
