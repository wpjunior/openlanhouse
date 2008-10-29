# coding: utf-8
#
# SearchEntry - An enhanced search entry with alternating background colouring 
#               and timeout support
#
# Copyright (C) 2007 Sebastian Heinlein
#               2007 Canonical Ltd.
#               2007 OpenLanhouse
#
# Authors:
#  Sebastian Heinlein <glatzor@ubuntu.com>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA

import gtk
import gobject

try:
    import sexy
    sexy_avail = True
    
except:
    sexy_avail = False
    
    class sexy: #Gambiarra
        class IconEntry:
            def __init__(self):
                pass


class SexyEntry(sexy.IconEntry, gobject.GObject):
    __gsignals__ = {'terms-changed':(gobject.SIGNAL_RUN_FIRST,
                                     gobject.TYPE_NONE,
                                     (gobject.TYPE_STRING,))}

    def __init__(self, icon_theme):
        """
        Creates an enhanced IconEntry that supports a time out when typing
        and uses a different background colour when the search is active
        """
        sexy.IconEntry.__init__(self)
        self.__gobject_init__()
        self._handler_changed = self.connect_after("changed",
                                                   self._on_changed)
        self.connect("icon-pressed", self._on_icon_pressed)
        
        image = gtk.Image()
        pixbuf = icon_theme.load_icon(gtk.STOCK_FIND,
                                      gtk.ICON_SIZE_MENU,
                                      0)
        image.set_from_pixbuf(pixbuf)
        
        image2 = gtk.Image()
        pixbuf2 = icon_theme.load_icon(gtk.STOCK_CLEAR,
                                      gtk.ICON_SIZE_MENU,
                                      0)
        image2.set_from_pixbuf(pixbuf2)
        
        self.set_icon(sexy.ICON_ENTRY_PRIMARY, image)
        self.set_icon(sexy.ICON_ENTRY_SECONDARY, image2)
        self.set_icon_highlight(sexy.ICON_ENTRY_SECONDARY, True)

        # Do not draw a yellow bg if an a11y theme is used
        settings = gtk.settings_get_default()
        theme = settings.get_property("gtk-theme-name")
        self._a11y = theme.startswith("HighContrast") or\
                     theme.startswith("LowContrast")

        self._timeout_id = 0

    def _on_icon_pressed(self, widget, icon, mouse_button):
        """
        Emit the terms-changed signal without any time out when the clear
        button was clicked
        """
        if icon == sexy.ICON_ENTRY_SECONDARY:
            self.handler_block(self._handler_changed)
            self.set_text("")
            self._check_style()
            self.handler_unblock(self._handler_changed)
            self.emit("terms-changed", self.get_text())

    def _on_changed(self, widget):
        """
        Call the actual search method after a small timeout to allow the user
        to enter a longer search term
        """
        self._check_style()
        if self._timeout_id > 0:
            gobject.source_remove(self._timeout_id)
        #FIXME: Could be of use for a11y
        #timeout = self.config.get_int("/apps/gnome-app-install/search-timeout")
        timeout = 1000
        self._timeout_id = gobject.timeout_add(timeout,
                            lambda: self.emit("terms-changed", self.get_text()))

    def _check_style(self):
        
        if self._a11y == True:
            return
        if self.get_text() == "":
            self.modify_base(gtk.STATE_NORMAL, None)
        else:
            self.modify_base(gtk.STATE_NORMAL,
                             gtk.gdk.Color(63479, 63479, 48830))

class NormalEntry(gtk.Entry, gobject.GObject):
    __gsignals__ = {'terms-changed':(gobject.SIGNAL_RUN_FIRST,
                                     gobject.TYPE_NONE,
                                     (gobject.TYPE_STRING,))}

    def __init__(self, icon_theme):
        """
        Creates an enhanced IconEntry that supports a time out when typing
        and uses a different background colour when the search is active
        """
        gtk.Entry.__init__(self)
        self.__gobject_init__()
        self._handler_changed = self.connect_after("changed",
                                                   self._on_changed)

        # Do not draw a yellow bg if an a11y theme is used
        settings = gtk.settings_get_default()
        theme = settings.get_property("gtk-theme-name")
        self._a11y = theme.startswith("HighContrast") or\
                     theme.startswith("LowContrast")

        self._timeout_id = 0

    def _on_icon_pressed(self, widget, icon, mouse_button):
        """
        Emit the terms-changed signal without any time out when the clear
        button was clicked
        """
        if icon == sexy.ICON_ENTRY_SECONDARY:
            self.handler_block(self._handler_changed)
            self.set_text("")
            self._check_style()
            self.handler_unblock(self._handler_changed)
            self.emit("terms-changed", self.get_text())

    def _on_changed(self, widget):
        """
        Call the actual search method after a small timeout to allow the user
        to enter a longer search term
        """
        self._check_style()
        if self._timeout_id > 0:
            gobject.source_remove(self._timeout_id)
        
        timeout = 1000
        self._timeout_id = gobject.timeout_add(timeout,
                            lambda: self.emit("terms-changed", self.get_text()))

    def _check_style(self):
        """
        Use a different background colour if a search is active
        """
        # Based on the Rhythmbox code
        yellowish = gtk.gdk.Color(63479, 63479, 48830)
        if self._a11y == True:
            return
        if self.get_text() == "":
            self.modify_base(gtk.STATE_NORMAL, None)
        else:
            self.modify_base(gtk.STATE_NORMAL, yellowish)


if sexy_avail:
    SearchEntry = SexyEntry
else:
    SearchEntry = NormalEntry
