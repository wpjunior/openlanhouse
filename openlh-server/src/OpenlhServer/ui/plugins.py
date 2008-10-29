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
import gtk

from OpenlhServer.ui.utils import get_gtk_builder
from OpenlhServer.globals import _
from OpenlhServer.plugins import __all__ as ALL_PLUGINS

from OpenlhServer.plugins import get_plugin, get_plugin_name, get_plugin_author
from OpenlhServer.plugins import get_plugin_description, get_plugin_copyright
from OpenlhServer.plugins import get_plugin_site

class PluginsWindow:
    
    iters = {}
    
    def __init__(self, MainWindow=None, Daemon=None, Parent=None):
        """
            @MainWindow:
                must be a OpenlhServer.ui.main.Manager object
        """
        self.daemon = Daemon
        self.mainwindow = MainWindow
        
        self.xml = get_gtk_builder('plugins')
        self.dialog = self.xml.get_object('dialog')
        self.treeview = self.xml.get_object('treeview')
        
        self.title = self.xml.get_object('title')
        self.description = self.xml.get_object('description')
        self.author = self.xml.get_object('author')
        self.copyright = self.xml.get_object('copyright')
        self.site = self.xml.get_object('site')
        self.preferences_button = self.xml.get_object('preferences_button')
        
        #TreeView Model: plugin name, activated, Description
        self.ListStore = gtk.ListStore(gobject.TYPE_STRING,
                                       gobject.TYPE_BOOLEAN,
                                       gobject.TYPE_STRING)
        
        #Columns
        #Enabled
        crt = gtk.CellRendererToggle()
        crt.set_property('activatable', True)
        crt.connect('toggled', self.on_enabled_toggled, self.ListStore)

        column = gtk.TreeViewColumn(_("Enabled"), crt, active=1)
        column.set_reorderable(False)
        column.set_clickable(False)
        column.set_resizable(False)
        column.set_expand(False)
        
        self.treeview.append_column(column)
        
        #Plugin Name
        column = gtk.TreeViewColumn(_("Plugin"), gtk.CellRendererText(), text=2)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_reorderable(True)
        column.set_clickable(True)
        column.set_sort_column_id(2)
        column.set_resizable(True)
        column.set_expand(True)
        
        self.treeview.append_column(column)
        
        self.treeview.set_model(self.ListStore)
        
        self.xml.connect_signals(self)
        
        if Parent:
            self.dialog.set_transient_for(Parent)
    
    def clear_entries(self):
        """
            Clear all panel entries
        """
        
        for i in self.title, self.description, self.author, self.copyright:
            i.set_text("")
        
        self.site.set_label("")
        self.site.set_uri("")
        
        self.preferences_button.set_sensitive(False)
    
    def update_plugin_descriptions(self):
        """
            Update all informations located in right panel
        """
        
        self.clear_entries()
        
        if len(self.ListStore) > 0:
            model_ = self.ListStore
            if self.treeview.get_cursor()[0]:
                index = self.treeview.get_cursor()[0][0]
            else:
                index = 0
            
            plugin_module_name = model_[index][0]
            plugin = get_plugin(plugin_module_name)
            
            plugin_name = get_plugin_name(plugin)
            plugin_description = get_plugin_description(plugin)
            plugin_author = get_plugin_author(plugin)
            plugin_copyright = get_plugin_copyright(plugin)
            plugin_site = get_plugin_site(plugin)
            
            self.title.set_markup("<big><big>%s</big></big>" % plugin_name)
            
            if plugin_description:
                self.description.set_text(plugin_description)
            
            if plugin_author:
                self.author.set_text(plugin_author)
            
            if plugin_copyright:
                self.copyright.set_text(plugin_copyright)
            
            if plugin_site:
                self.site.set_label(plugin_site)
                self.site.set_uri(plugin_site)
            
            self.preferences_button.set_sensitive(hasattr(plugin, "configure"))
    
    def on_cursor_changed(self, obj):
        self.update_plugin_descriptions()
    
    def on_enabled_toggled(self, cell, path, model, *args):
        if not model[path][1]:
            #enable plugin
            self.daemon.enable_plugin(model[path][0], self.mainwindow)
        else:
            #disable plugin
            self.daemon.disable_plugin(model[path][0], self.mainwindow)
        
        model[path][1] = not model[path][1]
    
    def on_preferences_clicked(self, obj):
        
        if len(self.ListStore) > 0:
            model_ = self.ListStore
            if self.treeview.get_cursor()[0]:
                index = self.treeview.get_cursor()[0][0]
            else:
                index = 0
            
            plugin_module_name = model_[index][0]
            plugin = get_plugin(plugin_module_name)
            
            plugin.configure(self.daemon, self.mainwindow)
    
    def populate_plugins(self):
        """
            Populate plugins treeview
        """
        
        for i in ALL_PLUGINS:
            plugin = get_plugin(i)
            plugin_name = get_plugin_name(plugin)
            plugin_enabled = self.daemon.plugin_is_enabled(i)
            
            if not plugin_name:
                plugin_name = i
            
            iter = self.ListStore.append((i, plugin_enabled, plugin_name))
            self.iters[plugin_name] = iter
    
    def run(self):
        self.populate_plugins()
        self.update_plugin_descriptions()
        self.dialog.run()
        self.dialog.destroy()