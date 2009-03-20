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

from OpenlhCore.ConfigClient import get_default_client
from OpenlhServer.globals import *
import gettext
_ = gettext.gettext

TEXT_CELL_RENDER, PIXMAP_CELL_RENDER, PROGRESS_CELL_RENDER = range(3)

CELLRENDERS = (gtk.CellRendererText,
               gtk.CellRendererPixbuf,
               gtk.CellRendererProgress)


(MACHINE_CEL_ID,
 MACHINE_CEL_PIXMAP,
 MACHINE_CEL_SOURCE,
 MACHINE_CEL_HOST,
 MACHINE_CEL_USER,
 MACHINE_CEL_TIME,
 MACHINE_CEL_TIME_ELAPSED,
 MACHINE_CEL_TIME_ELAPSED_PROGRESS,
 MACHINE_CEL_REMAING,
 MACHINE_CEL_PROGRESS,
 MACHINE_CEL_PAY) = range(11)

(USERS_CEL_ID,
 USERS_CEL_NICK,
 USERS_CEL_NAME,
 USERS_CEL_EMAIL,
 USERS_CEL_CREDIT) = range(5)
        
(CASH_FLOW_CEL_DAY,
 CASH_FLOW_CEL_HOUR,
 CASH_FLOW_CEL_TYPE,
 CASH_FLOW_CEL_USER_NAME,
 CASH_FLOW_CEL_DESC,
 CASH_FLOW_CEL_VALUE) = range(6)

(OPEN_DEBTS_CEL_ID,
 OPEN_DEBTS_CEL_DAY,
 OPEN_DEBTS_CEL_MACHINE,
 OPEN_DEBTS_CEL_START_TIME,
 OPEN_DEBTS_CEL_END_TIME,
 OPEN_DEBTS_CEL_USER_NAME,
 OPEN_DEBTS_CEL_DESC,
 OPEN_DEBTS_CEL_VALUE) = range(8)

(OPEN_DEBTS_OTHER_CEL_ID,
 OPEN_DEBTS_OTHER_CEL_DAY,
 OPEN_DEBTS_OTHER_CEL_TIME,
 OPEN_DEBTS_OTHER_CEL_USER_NAME,
 OPEN_DEBTS_OTHER_CEL_DESC,
 OPEN_DEBTS_OTHER_CEL_VALUE) = range(6)

MACHINE_SEARCHABLE_COLS = (MACHINE_CEL_HOST, MACHINE_CEL_USER)
USER_SEARCHABLE_COLS = (USERS_CEL_NICK, USERS_CEL_NAME, USERS_CEL_EMAIL)
CASH_FLOW_SEARCHABLE_COLS = (CASH_FLOW_CEL_HOUR, CASH_FLOW_CEL_TYPE,
                             CASH_FLOW_CEL_USER_NAME, CASH_FLOW_CEL_DESC)

OPEN_DEBTS_SEARCHABLE_COLS = range(8)
OPEN_DEBTS_OTHER_SEARCHABLE_COLS = range(6)

class common:
    
    text_filter = ""
    
    def __init__(self, conf_lists_path):
        """
            Constructor common properties
        """
        self.conf_client = get_default_client()
        
        self.active_lists = self.conf_client.get_string_list(conf_lists_path)
        
        self.conf_lists_path = conf_lists_path
        self.store = None
        self.filter = None
        self.renders=[]
        self.columns=[]
        self.dataTypes=[]
        self.search_cols = []
        self.treemenu = gtk.Menu()
        
    def get_columns(self):
        return self.columns
    
    def get_treemenu(self):
        return self.treemenu
        
    def get_renders(self):
        return self.renders
    
    def get_list_store(self):
        if not self.store:
            if self.dataTypes:
                self.store = gtk.ListStore(*self.dataTypes)
        
        return self.store
    
    def get_filter(self):
        if self.store:
            if not self.filter:
                self.filter = self.store.filter_new()
        
        return self.filter
            
    def clear(self):
        
        self.store = None
        self.filter = None
        self.renders = []
        self.columns = []
        self.dataTypes = []
        
    def make_column(self, low_name, title, columnId, cel_num, min_size=None,
                    max_size=None, xalign=None, expand=False, resizable=True):
        
        datatype1 = None
        datatype2 = None
        
        render = CELLRENDERS[columnId]()
        
        if xalign:
            render.set_property('xalign', xalign)
        
        if columnId == TEXT_CELL_RENDER:
            column = gtk.TreeViewColumn(title, render, markup=cel_num)
            datatype1 = gobject.TYPE_STRING
            self.search_cols.append(cel_num)
            
        elif columnId == PIXMAP_CELL_RENDER:
            column = gtk.TreeViewColumn(title, render, pixbuf=cel_num)
            datatype1 = gtk.gdk.Pixbuf
        
        elif columnId == PROGRESS_CELL_RENDER:
            column = gtk.TreeViewColumn(title, render, text=cel_num ,value=cel_num + 1)
            datatype1 = gobject.TYPE_STRING
            datatype2 = gobject.TYPE_INT
            
        else:
            return False
        
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_reorderable(True)
        column.set_clickable(True)
        column.set_sort_column_id(cel_num)
        column.set_resizable(resizable)
        column.set_expand(expand)
        
        if low_name:
            column_menu = gtk.CheckMenuItem(label=title, use_underline=True)
            self.treemenu.append(column_menu)
            
            stt = low_name in self.active_lists
            column.set_visible(stt)
            column_menu.set_active(stt)
            
            column_menu.connect("toggled", self.set_visible_column,
                                column, (low_name, cel_num))
            
            column_menu.show()
        
        if min_size:
            column.set_min_width(min_size)
        
        if max_size:
            column.set_max_width(max_size)

        if xalign:
            column.set_alignment(xalign)
        
        self.renders.insert(cel_num, render)
        self.columns.insert(cel_num, column)
        
        if datatype1:
            self.dataTypes.append(datatype1)
        
        if datatype2:
            self.dataTypes.append(datatype2)
        
        return column
        
    def start_filter(self, text):
        
        self.text_filter = text
        
        if self.text_filter:
            self.filter.refilter()
    
    def set_visible_column(self, obj, column, list):
        low_name, cel_num = list
        
        status = obj.get_active()
        
        if status:
            self.active_lists.insert(cel_num, low_name)
        else:
            self.active_lists.remove(low_name)
        
        self.conf_client.set_string_list(self.conf_lists_path,
                                         self.active_lists)
        
        column.set_property('visible', status)

class machine(common):
    def __init__(self):
        
        common.__init__(self, 'ui/machines_columns')
        
        self.make_column('id', _('ID'), TEXT_CELL_RENDER,
                                            MACHINE_CEL_ID, None, max_size=100)
        self.make_column(None, ' ', PIXMAP_CELL_RENDER,
                                            MACHINE_CEL_PIXMAP, resizable=False)
        self.make_column('source', _('Source'), TEXT_CELL_RENDER,
                                            MACHINE_CEL_SOURCE, None, expand=False)
        self.make_column('host', _('Host'), TEXT_CELL_RENDER,
                                            MACHINE_CEL_HOST, None, expand=True)
        self.make_column('user', _('User'), TEXT_CELL_RENDER,
                                            MACHINE_CEL_USER, None, expand=True)
        self.make_column('time', _('Time'), TEXT_CELL_RENDER,
                                            MACHINE_CEL_TIME, 80)
        self.make_column('time_elapsed', _('Time elapsed'), PROGRESS_CELL_RENDER,
                                            MACHINE_CEL_TIME_ELAPSED, 80)
        self.make_column('time_last', _('Time left'), PROGRESS_CELL_RENDER,
                                            MACHINE_CEL_REMAING, None)
        self.make_column('total_to_pay', _('Total to pay'), TEXT_CELL_RENDER,
                                            MACHINE_CEL_PAY, None, xalign=1.0)
        
        self.treemnu = self.get_treemenu()

class users(common):
    def __init__(self):
        
        common.__init__(self, 'ui/users_columns')
        
        self.make_column('id', _('ID'), TEXT_CELL_RENDER,
                                            USERS_CEL_ID, 60)
        self.make_column('nick', _('Nick'), TEXT_CELL_RENDER,
                                            USERS_CEL_NICK, 100)
        self.make_column('name', _('Name'), TEXT_CELL_RENDER,
                                            USERS_CEL_NAME, None, expand=True)
        self.make_column('email', _('Email'), TEXT_CELL_RENDER,
                                            USERS_CEL_EMAIL, None,
                                            xalign=1.0, expand=True)
        self.make_column('credit', _('Credit'),
                                            TEXT_CELL_RENDER,
                                            USERS_CEL_CREDIT, 100, xalign=1.0)
        
        self.treemnu = self.get_treemenu()

class cash_flow(common):
    def __init__(self):
        
        common.__init__(self, 'ui/cash_flow_columns')
        
        self.make_column('day', _('Day'), TEXT_CELL_RENDER,
                                            CASH_FLOW_CEL_DAY, 80)
        self.make_column('hour', _('Hour'), TEXT_CELL_RENDER,
                                            CASH_FLOW_CEL_HOUR, 70)
        self.make_column('type', _("Type"), TEXT_CELL_RENDER,
                                            CASH_FLOW_CEL_TYPE, 100)
        self.make_column('user', _('User'), TEXT_CELL_RENDER,
                                            CASH_FLOW_CEL_USER_NAME,
                                            None, expand=True)
        self.make_column('description', _('Notes'), TEXT_CELL_RENDER,
                                            CASH_FLOW_CEL_DESC,
                                            None, expand=True)
        self.make_column('value', _('Value'), TEXT_CELL_RENDER,
                                            CASH_FLOW_CEL_VALUE,
                                            50, 100, xalign=1.0)
        
        self.treemnu = self.get_treemenu()

class open_debts_machine(common):
    def __init__(self):
        
        common.__init__(self, 'ui/open_debts_machine_columns')
        
        self.make_column('id', _('ID'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_CEL_ID, 60)
        self.make_column('day', _('Day'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_CEL_DAY, 80)
        self.make_column('machine', _('Machine'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_CEL_MACHINE)
        self.make_column('start_time', _('Start time'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_CEL_START_TIME, 70)
        self.make_column('end_time', _('End time'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_CEL_END_TIME, 70)
        self.make_column('user', _('User'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_CEL_USER_NAME,
                                            None, expand=True)
        self.make_column('description', _('Notes'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_CEL_DESC,
                                            None, expand=True)
        self.make_column('value', _('Value'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_CEL_VALUE,
                                            50, 100, xalign=1.0)
        
        self.treemnu = self.get_treemenu()

class open_debts_other(common):
    def __init__(self):
        
        common.__init__(self, 'ui/open_debts_other_columns')
        
        self.make_column('id', _('ID'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_OTHER_CEL_ID, 60)
        self.make_column('day', _('Day'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_OTHER_CEL_DAY, 80)
        self.make_column('time', _('Time'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_OTHER_CEL_TIME, 70)
        self.make_column('user', _('User'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_OTHER_CEL_USER_NAME,
                                            None, expand=True)
        self.make_column('description', _('Notes'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_OTHER_CEL_DESC,
                                            None, expand=True)
        self.make_column('value', _('Value'), TEXT_CELL_RENDER,
                                            OPEN_DEBTS_OTHER_CEL_VALUE,
                                            50, 100, xalign=1.0)
        
        self.treemnu = self.get_treemenu()
        
