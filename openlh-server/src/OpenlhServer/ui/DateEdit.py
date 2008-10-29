# Python GTK+ date and time entry widget.
# Copyright (C) 2005  Fabian Sturm
#
# ported from the libgnomeui/gnome-dateedit.c
# with changes where it makes sense for python (e.g. return types)
#
# This widget is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this widget; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import sys
import time
import datetime

import pygtk
pygtk.require('2.0')
import gobject
import gtk
from gtk import gdk

DATE_EDIT_WEEK_STARTS_ON_MONDAY = 1 << 2
 
 # gnome_date_edit_new:
 # @the_time: date and time to be displayed on the widget
 #
 # Description: Creates a new #GnomeDateEdit widget which can be used
 # to provide an easy to use way for entering dates and times.
 # If @the_time is 0 then current time is used.
 #
 # Returns: a new #GnomeDateEdit widget.
 # Todo: missing the version with the flags in the constructor

class DateEdit(gtk.HBox):
    __gtype_name__ = 'DateEdit'
    
    __gproperties__ = {
        'time' : (gobject.TYPE_PYOBJECT,                     # type
                  'Time',                                    # nick name
                  'The time currently selected',             # description
                  gobject.PARAM_READWRITE),                  # flags
                  
        'initial_time' : (gobject.TYPE_PYOBJECT,
                  'Initial Time',
                  'The initial time',
                  gobject.PARAM_READABLE)
    }

    __gsignals__ = {
        'time_changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          ()),
        'date_changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          ()),                          
    
    }

    def __init__(self, the_time = None):
        gtk.HBox.__init__(self)

        # preset values
        self.__flags = None

        # the date entry
        self.__date_entry = gtk.Entry()
        self.__date_entry.set_size_request(80, -1)
        self.pack_start(self.__date_entry, True, True, 0)
        self.__date_entry.show()
        self.__date_entry.connect("activate", self.on_date_entry_activate)
        
        # the date button
        self.__date_button = gtk.Button()
        self.__date_button.connect('clicked', self.date_button_clicked)
        self.pack_start(self.__date_button, False, False, 0)
        
        # the down arrow
        arrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_OUT)
        self.__date_button.add(arrow)
        arrow.show()
        
        # finally show the button
        self.__date_button.show()
        
        # the calendar popup
        self.__cal_popup = gtk.Window(gtk.WINDOW_POPUP)
        self.__cal_popup.set_events(self.__cal_popup.get_events() |
                                                    gdk.KEY_PRESS_MASK)
        self.__cal_popup.connect('delete_event', self.delete_popup)
        self.__cal_popup.connect('key_press_event', self.key_press_popup)
        self.__cal_popup.connect('button_press_event', self.button_press_popup)
        self.__cal_popup.set_resizable(False) # Todo: Needed?
        
        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_OUT)
        self.__cal_popup.add(frame)
        frame.show()
        
        # the calendar
        self.__calendar = gtk.Calendar()
        self.__calendar.display_options(gtk.CALENDAR_SHOW_DAY_NAMES 
                                        | gtk.CALENDAR_SHOW_HEADING)
        
        self.__calendar.connect('day-selected', self.day_selected)
        self.__calendar.connect('day-selected-double-click',
                                    self.day_selected_double_click)
        frame.add(self.__calendar)
        self.__calendar.show()
        
        # set provided date and time
        self.set_time(the_time)
        
    def get_internal_calendar(self):
        return self.__calendar
        
    def popup_grab_on_window(self, window, activate_time):
        if gdk.pointer_grab(window, True, gdk.BUTTON_PRESS_MASK 
                                          | gdk.BUTTON_RELEASE_MASK
                                          | gdk.POINTER_MOTION_MASK, 
                            None, None, activate_time) == 0:
                if gdk.keyboard_grab (window, True, activate_time) == 0:
                    return True
                else:
                    gdk.pointer_ungrab(activate_time)
                    return False
        return False


    def position_popup(self):
        req = self.__cal_popup.size_request()
        (x,y) = gdk.Window.get_origin(self.__date_button.window)

        x += self.__date_button.allocation.x
        y += self.__date_button.allocation.y
        bwidth = self.__date_button.allocation.width
        bheight = self.__date_button.allocation.height

        x += bwidth - req[0]
        y += bheight

        if x < 0: x = 0
        if y < 0: y = 0
        
        self.__cal_popup.move(x,y)
        
        
    def date_button_clicked(self, widget, data=None):
        # Temporarily grab pointer and keyboard on a window we know exists        
        if not self.popup_grab_on_window(widget.window,
                                gtk.get_current_event_time()):
            
            print 'error during grab'
            return
        
        # set calendar date
        str = self.__date_entry.get_text()
        mtime = time.strptime(str, '%x')
        self.__calendar.select_month(mtime.tm_mon - 1, mtime.tm_year)
        self.__calendar.select_day(mtime.tm_mday)        
        
        # position and show popup window
        self.position_popup()
        self.__cal_popup.grab_add()
        self.__cal_popup.show()
        self.__calendar.grab_focus()
        
        # Now transfer our grabs to the popup window, this should always succed
        self.popup_grab_on_window(self.__cal_popup.window, gtk.get_current_event_time())

    def hide_popup(self):
        self.__cal_popup.hide()
        self.__cal_popup.grab_remove()

    def day_selected(self, widget, data=None):
        (year, month, day) = self.__calendar.get_date()
        
        month += 1
        the_time = datetime.date(year, month, day)
        self.__date_entry.set_text(the_time.strftime('%x'))
        self.emit('date-changed')
        
    def on_date_entry_activate(self, obj):
        try:
            mdate = time.strptime(obj.get_text(), '%x')
            self.__calendar.select_month(mdate.tm_mon - 1, mdate.tm_year)
            self.__calendar.select_day(mdate.tm_mday) 
        except:
            (year, month, day) = self.__calendar.get_date()
            month += 1
            the_time = datetime.date(year, month, day)
            self.__date_entry.set_text(the_time.strftime('%x'))
            self.emit('date-changed')
    
    def day_selected_double_click(self, widget, data=None):
        self.hide_popup()

    def key_press_popup(self, widget, data=None):        
        # Todo, Fixme: what is the name of gdk.Escape? missing?
        if data == None or data.keyval != 65307:
            return False

        # Todo: does not work and what does it do anyway?
        # widget.stop_emission_by_name('key_press_event')
        self.hide_popup()
        return True


    # Todo: is this correct?
    def button_press_popup(self, widget, data=None):
        # We don't ask for button press events on the grab widget, so
        # if an event is reported directly to the grab widget, it must
        # be on a window outside the application (and thus we remove
        # the popup window). Otherwise, we check if the widget is a child
        # of the grab widget, and only remove the popup window if it
        # is not.
        if data == None or data.window == None:
            return False
            
        child = data.window.get_user_data()
        if child != widget:
            while child:
                if child == widget:
                    return False
                child = child.parent
                
        self.hide_popup()
        return True


    def delete_popup(self, widget, data=None):
        # Todo: when is this ever called??
        print 'delete_popup'
        self.hide_popup();
        return TRUE;
        
    def time_selected(self, widget, data = None):
        self.__time_entry.set_text(data)
        self.emit('time-changed');
        
        
    # properties and their convenience functions    
        
    def get_time(self):
        str = self.__date_entry.get_text()
        mdate = time.strptime(str, '%x')
        
        return (mdate.tm_year, mdate.tm_mon, mdate.tm_mday)
        
    def set_time(self, the_time):
        if the_time is None:
            the_time = datetime.datetime.today()
        else:
            assert len(the_time) == 3 and isinstance(the_time, (tuple, list))
            the_time = datetime.datetime(*the_time)
        
        assert isinstance(the_time, (datetime.datetime, datetime.date))
        
        self.__initial_time = the_time
        self.__date_entry.set_text(the_time.strftime('%x'))


    # Changes the display flags on an existing date editor widget
    def set_flags(self, flags):
        old_flags = self.__flags
        self.__flags = flags
        
        if (flags & DATE_EDIT_WEEK_STARTS_ON_MONDAY) is (old_flags & DATE_EDIT_WEEK_STARTS_ON_MONDAY):
            if flags & DATE_EDIT_WEEK_STARTS_ON_MONDAY:
                self.__calendar.set_display_options(self.__calendar.get_display_options() | gtk.CALENDAR_WEEK_START_MONDAY)
            else:
                self.__calendar.set_display_options(self.__calendar.get_display_options() & ~gtk.CALENDAR_WEEK_START_MONDAY)
        
    def get_initial_time(self):
        return self.__initial_time
        
    # get_properties
    def do_get_property(self, property): 
        if property.name == 'time':            
            return self.get_time()
        elif property.name == 'dateedit-flags':
            return self.__flags
        elif property.name == 'initial-time':
            return self.get_initial_time()
        else:
            raise AttributeError, 'unknown property %s' % property.name
            
    # set_properties
    def do_set_property(self, property, value):
        if property.name == 'time':
            self.set_time(value)            
        elif property.name == 'dateedit-flags':
            self.set_flags(value)
        else:
            raise AttributeError, 'unknown property %s' % property.name
            
        
# finally register our new Type        
# Warning, throws an error if a type_flags property is register 
# see bug number #323290
gobject.type_register(DateEdit)

