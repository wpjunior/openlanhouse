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

import os
import gtk
import gobject

try:
    import pynotify
    notify_daemon_support = True
except:
    pynotify = None
    notify_daemon_support = False

def popup_init(name):
    # Notification daemon support
    if notify_daemon_support:
        if not pynotify.is_initted():
            if not pynotify.init(name):
                global notify_daemon_support
                notify_daemon_support = False

BG_COLOR = "white"
POS_X = 0
POS_Y = 0

class PopupManager:
    popups_notification_height = 0
    popup_notification_windows = []

popup_manager = PopupManager()

class PopupNotificationWindow:
    def __init__(self, title=None, path_to_image=None, 
                 text=None, bg_color=BG_COLOR, timeout=8000):
        xml = gtk.Builder()
        xml.add_from_file('popup_notification_window.ui')
        
        self.window = xml.get_object('popup_notification_window')

        if gtk.gtk_version >= (2, 10, 0) and gtk.pygtk_version >= (2, 10, 0):
                self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_TOOLTIP)

        close_button = xml.get_object('close_button')
        event_type_label = xml.get_object('event_type_label')
        event_description_label = xml.get_object('event_description_label')
        eventbox = xml.get_object('eventbox')
        image = xml.get_object('notification_image')
            
        if not text:
            text = ''
        if not title:
            title = ''

        event_type_label.set_markup(
                '<span foreground="black" weight="bold">%s</span>' %
                gobject.markup_escape_text(title))

        # set colors [ http://www.pitt.edu/~nisg/cis/web/cgi/rgb.html ]
        self.window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))

        popup_bg_color = gtk.gdk.color_parse(bg_color)
        close_button.modify_bg(gtk.STATE_NORMAL, popup_bg_color)
        eventbox.modify_bg(gtk.STATE_NORMAL, popup_bg_color)
        event_description_label.set_markup('<span foreground="black">%s</span>' %
                                           gobject.markup_escape_text(text))

        # set the image
        image.set_from_file(path_to_image)

        # position the window to bottom-right of screen
        window_width, self.window_height = self.window.get_size()
        popup_manager.popups_notification_height += self.window_height
		
        pos_x = gtk.gdk.screen_width() - window_width + 1 + POS_X
        pos_y = gtk.gdk.screen_height() - \
            popup_manager.popups_notification_height + 1 + POS_Y
        self.window.move(pos_x, pos_y)
		
        xml.connect_signals(self)
        self.window.show_all()
        gobject.timeout_add(timeout, self.on_timeout)
            
        popup_manager.popup_notification_windows.append(self)

    def on_close_button_clicked(self, widget):
        self.adjust_height_and_move_popup_notification_windows()

    def on_timeout(self):
        self.adjust_height_and_move_popup_notification_windows()

    def adjust_height_and_move_popup_notification_windows(self):
        # remove
        popup_manager.popups_notification_height -= self.window_height
        self.window.destroy()

        if len(popup_manager.popup_notification_windows) > 0:
            # we want to remove the first window added in the list
            popup_manager.popup_notification_windows.pop(0)

        # move the rest of popup windows
        popup_manager.popups_notification_height = 0
        for window_instance in popup_manager.popup_notification_windows:
            window_width, window_height = window_instance.window.get_size()
            popup_manager.popups_notification_height += window_height
            window_instance.window.move(gtk.gdk.screen_width() - window_width,
                                        gtk.gdk.screen_height() - \
                                                popup_manager.popups_notification_height)

    def on_popup_notification_window_button_press_event(self, widget, event):
        if event.button != 1:
                self.window.destroy()
                return
        self.adjust_height_and_move_popup_notification_windows()

if notify_daemon_support:
    class NotificationDaemonWindow:
        def __init__(self, title=None, text=None, 
                     path_to_image=None, bg_color=BG_COLOR,
                     timeout=5000):
            self.notification = pynotify.Notification(title, text, path_to_image)
            self.notification.set_timeout(timeout)
            self.notification.show()

if notify_daemon_support:
    Popup = NotificationDaemonWindow
else:
    Popup = PopupNotificationWindow

if __name__ == "__main__":
    Popup(title="macumbaria", path_to_image="/usr/share/icons/hicolor/48x48/apps/devhelp.png")
    Popup(title="macumbaria", path_to_image="/usr/share/icons/hicolor/48x48/apps/emacs.png")
    Popup(title="macumbaria", path_to_image="/usr/share/icons/hicolor/48x48/apps/emacs.png")
    Popup(title="Teste", text="<b>t</b>estando")
    gobject.timeout_add_seconds(2, Popup, "macumbaria", "teste")
    gtk.main()
