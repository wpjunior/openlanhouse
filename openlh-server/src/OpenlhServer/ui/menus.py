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

from OpenlhServer.globals import *
_ = gettext.gettext

class common(gtk.Menu):
    
    menus = []
    
    def __init__(self):
        gtk.Menu.__init__(self)
        
    def add_menu_item(self, name=None, label=None, tooltip=None, stock_id=None):
        
        menuAction = gtk.Action(name, label, tooltip, stock_id)
        menuItem = menuAction.create_menu_item()
        
        menuItem.show()
        self.append(menuItem)
        self.menus.append(menuItem)
        return menuItem
    
    def add_separator(self):
        menuItem = gtk.SeparatorMenuItem()
        menuItem.show()
        self.append(menuItem)

class machine(common):
    def __init__(self):
        common.__init__(self)
        self.unblock = self.add_menu_item(label=_('Unblock'),
                                          stock_id=gtk.STOCK_YES)
        
        self.block = self.add_menu_item(label=_('Block'), 
                                        stock_id=gtk.STOCK_NO)
        
        self.add_separator()
        self.addtime = self.add_menu_item(label=_('_Add Time'),
                                            stock_id=gtk.STOCK_ADD)
        
        self.deltime = self.add_menu_item(label=_('_Remove Time'),
                                           stock_id=gtk.STOCK_REMOVE)
        
        self.add_separator()
        self.delete = self.add_menu_item(stock_id=gtk.STOCK_DELETE)
        self.edit = self.add_menu_item(stock_id=gtk.STOCK_EDIT)
        self.add_separator()
        self.properties = self.add_menu_item(stock_id=gtk.STOCK_PROPERTIES)

class users(common):
    def __init__(self):
        common.__init__(self)
        
        self.addcredit = self.add_menu_item(label=_('_Add Credit'),
                                            stock_id=gtk.STOCK_ADD)
        
        self.delcredit = self.add_menu_item(label=_('_Remove Credit'),
                                           stock_id=gtk.STOCK_REMOVE)
        
        self.add_separator()
         
        self.change_pass = self.add_menu_item(label=_("Change password"))
        self.add_separator()
        self.delete = self.add_menu_item(stock_id=gtk.STOCK_DELETE)
        self.edit = self.add_menu_item(stock_id=gtk.STOCK_EDIT)
        self.add_separator()
        self.properties = self.add_menu_item(stock_id=gtk.STOCK_PROPERTIES)
