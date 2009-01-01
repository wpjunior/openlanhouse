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

global notify_daemon_support

try:
    import pynotify
    notify_daemon_support = True
except:
    pynotify = None
    notify_daemon_support = False

global notify_init
notify_init = False

def popup_init(name):
    # Notification daemon support
    global notify_init
    global notify_daemon_support
    if notify_daemon_support:
        if not pynotify.is_initted():
            if not pynotify.init(name):
                notify_daemon_support = False
                notify_init = False
            else:
                notify_init = True

BG_COLOR = "white"
POS_X = 0
POS_Y = 0

class PopupManager:
    popups_notification_height = 0
    popup_notification_windows = []

popup_manager = PopupManager()

XML_WINDOW = """\
<?xml version="1.0"?>
<!--*- mode: xml -*-->
<interface>
  <object class="GtkWindow" id="popup_notification_window">
    <property name="border_width">1</property>
    <property name="width_request">312</property>
    <property name="height_request">95</property>
    <property name="title" translatable="yes"/>
    <property name="type">GTK_WINDOW_POPUP</property>
    <property name="window_position">GTK_WIN_POS_NONE</property>
    <property name="modal">False</property>
    <property name="resizable">False</property>
    <property name="destroy_with_parent">False</property>
    <property name="decorated">False</property>
    <property name="skip_taskbar_hint">True</property>
    <property name="skip_pager_hint">True</property>
    <property name="type_hint">GDK_WINDOW_TYPE_HINT_NORMAL</property>
    <property name="gravity">GDK_GRAVITY_SOUTH_EAST</property>
    <property name="focus_on_map">True</property>
    <property name="urgency_hint">False</property>
    <signal handler="on_popup_notification_window_button_press_event" name="button_press_event"/>
    <child>
      <object class="GtkEventBox" id="eventbox">
        <property name="visible">True</property>
        <property name="visible_window">True</property>
        <property name="above_child">False</property>
        <child>
          <object class="GtkHBox" id="hbox3019">
            <property name="border_width">4</property>
            <property name="visible">True</property>
            <property name="homogeneous">False</property>
            <property name="spacing">6</property>
            <child>
              <object class="GtkImage" id="notification_image">
                <property name="width_request">68</property>
                <property name="height_request">86</property>
                <property name="visible">True</property>
                <property name="xalign">0.5</property>
                <property name="yalign">0.5</property>
                <property name="xpad">0</property>
                <property name="ypad">0</property>
              </object>
              <packing>
                <property name="padding">0</property>
                <property name="expand">False</property>
                <property name="fill">False</property>
              </packing>
            </child>
            <child>
              <object class="GtkVBox" id="vbox111">
                <property name="visible">True</property>
                <property name="homogeneous">False</property>
                <property name="spacing">0</property>
                <child>
                  <object class="GtkHBox" id="hbox3020">
                    <property name="visible">True</property>
                    <property name="homogeneous">False</property>
                    <property name="spacing">0</property>
                    <child>
                      <object class="GtkLabel" id="event_type_label">
                        <property name="width_request">196</property>
                        <property name="visible">True</property>
                        <property name="label">Event Type</property>
                        <property name="use_underline">False</property>
                        <property name="use_markup">True</property>
                        <property name="justify">GTK_JUSTIFY_LEFT</property>
                        <property name="wrap">True</property>
                        <property name="selectable">False</property>
                        <property name="xalign">0.5</property>
                        <property name="yalign">0.5</property>
                        <property name="xpad">0</property>
                        <property name="ypad">0</property>
                        <property name="ellipsize">PANGO_ELLIPSIZE_NONE</property>
                        <property name="width_chars">-1</property>
                        <property name="single_line_mode">False</property>
                        <property name="angle">0</property>
                      </object>
                      <packing>
                        <property name="padding">0</property>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="close_button">
                        <property name="visible">True</property>
                        <property name="relief">GTK_RELIEF_NONE</property>
                        <property name="focus_on_click">True</property>
                        <signal handler="on_close_button_clicked" last_modification_time="Tue, 12 Apr 2005 12:48:32 GMT" name="clicked"/>
                        <child>
                          <object class="GtkImage" id="image496">
                            <property name="visible">True</property>
                            <property name="stock">gtk-close</property>
                            <property name="icon_size">1</property>
                            <property name="xalign">0.5</property>
                            <property name="yalign">0.5</property>
                            <property name="xpad">0</property>
                            <property name="ypad">0</property>
                          </object>
                        </child>
                      </object>
                      <packing>
                        <property name="padding">0</property>
                        <property name="expand">False</property>
                        <property name="fill">False</property>
                      </packing>
                    </child>
                  </object>
                  <packing>
                    <property name="padding">0</property>
                    <property name="expand">False</property>
                    <property name="fill">True</property>
                  </packing>
                </child>
                <child>
                  <object class="GtkLabel" id="event_description_label">
                    <property name="width_request">218</property>
                    <property name="height_request">64</property>
                    <property name="visible">True</property>
                    <property name="label">Event desc</property>
                    <property name="use_underline">False</property>
                    <property name="use_markup">False</property>
                    <property name="justify">GTK_JUSTIFY_LEFT</property>
                    <property name="wrap">True</property>
                    <property name="selectable">False</property>
                    <property name="xalign">0.5</property>
                    <property name="yalign">0.5</property>
                    <property name="xpad">0</property>
                    <property name="ypad">0</property>
                    <property name="ellipsize">PANGO_ELLIPSIZE_NONE</property>
                    <property name="width_chars">-1</property>
                    <property name="single_line_mode">False</property>
                    <property name="angle">0</property>
                  </object>
                  <packing>
                    <property name="padding">0</property>
                    <property name="expand">True</property>
                    <property name="fill">True</property>
                  </packing>
                </child>
              </object>
              <packing>
                <property name="padding">0</property>
                <property name="expand">True</property>
                <property name="fill">True</property>
              </packing>
            </child>
          </object>
        </child>
      </object>
    </child>
  </object>
</interface>
"""

class PopupNotificationWindow:
    def __init__(self, title=None, path_to_image=None, 
                 text=None, bg_color=BG_COLOR, timeout=8000):
        xml = gtk.Builder()
        xml.add_from_string(XML_WINDOW)
        
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
            if not notify_init:
                raise ProgrammingError, "Please init pynotify with 'popup_init'"

            self.notification = pynotify.Notification(title, text, path_to_image)
            self.notification.set_timeout(timeout)
            self.notification.show()

if notify_daemon_support:
    Popup = NotificationDaemonWindow
else:
    Popup = PopupNotificationWindow

if __name__ == "__main__":
    popup_init("openlh-teste")
    Popup(title="macumbaria", path_to_image="/usr/share/icons/hicolor/48x48/apps/devhelp.png")
    Popup(title="macumbaria", path_to_image="/usr/share/icons/hicolor/48x48/apps/emacs.png")
    Popup(title="macumbaria", path_to_image="/usr/share/icons/hicolor/48x48/apps/emacs.png")
    Popup(title="Teste", text="<b>t</b>estando")
    gobject.timeout_add_seconds(2, Popup, "macumbaria", "teste")
    gtk.main()
