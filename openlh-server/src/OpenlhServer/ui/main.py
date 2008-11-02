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
import gconf
import logging
import datetime

from time import localtime
from os import remove as os_remove

from OpenlhServer.ui.plugins import PluginsWindow

from OpenlhCore.utils import humanize_time
from OpenlhServer.ui import DateEdit, tray, icons, dialogs, treeview, prefs
from OpenlhServer.ui.SearchEntry import SearchEntry
from OpenlhCore.utils import md5_cripto
from OpenlhServer.ui.utils import get_gtk_builder
from OpenlhServer.utils import user_has_avatar, get_user_avatar_path
from OpenlhServer.db.models import CashFlowItem, User, MachineCategory
from OpenlhServer.globals import *
_ = gettext.gettext

class Manager:

    visible = False
    
    cash_flow_total_in = 0
    cash_flow_total_out = 0
    cash_flow_total = 0
    notebook_interative = True
    
    machines_iters = {}
    category_machines_iters = {}
    detect_machine_iters = {}
    users_iters = {}
    open_debts_machine_iters = {}
    open_debts_other_iters = {}
    machine_auth_pending = {}
    
    cash_flow_status_msg_id = 0
    
    machine_search_text = ""
    user_search_text = ""
    cash_flow_search_text = ""
    
    machine_filter_category = 0
    machine_filter_status = None
    
    def __init__(self, daemon):
        
        self.gconf_client = gconf.client_get_default()
        self.gconf_client.add_dir('/apps/openlh-server',
                                  gconf.CLIENT_PRELOAD_NONE)
        self.gconf_client.notify_add("/apps/openlh-server/ticket_suport",
                                     self.on_ticket_suport_cb)
        
        self.icons = icons.Icons()
        self.status_icons = icons.Icons(icon_path=STATUS_ICON_PATH)
        
        self.halt_icon = self.status_icons.get_icon("halt")
        self.available_icon = self.status_icons.get_icon("available")
        self.busy_icon = self.status_icons.get_icon("busy")
        
        self.daemon = daemon
        
        self.machine_manager = self.daemon.machine_manager
        self.machine_category_manager = self.daemon.machine_category_manager
        self.users_manager = self.daemon.users_manager
        self.cash_flow_manager = self.daemon.cash_flow_manager
        self.open_debts_machine_manager = self.daemon.open_debts_machine_manager
        self.open_debts_other_manager = self.daemon.open_debts_other_manager
        self.history_manager = self.daemon.history_manager
        
        self.instmachine_manager = self.daemon.instmachine_manager
        self.instmachine_manager.authorization_func = self.on_authorization_machine
        
        self.instmachine_manager.connect("new", self.on_new_machine)
        self.instmachine_manager.connect("delete", self.on_delete_machine)
        self.instmachine_manager.connect("update", self.on_update_machine)
        self.instmachine_manager.connect("update_total_to_pay",
                                         self.on_update_total_to_pay_machine)
        
        self.instmachine_manager.connect("status_changed", 
                                     self.on_machine_status_changed)
        
        self.logo = self.icons.get_icon(SERVER_ICON_NAME)
        
        #Widgets
        self.xml = get_gtk_builder("main")
        
        self.mainwindow = self.xml.get_object('mainwindow')
        self.new_machines = self.xml.get_object('new_machines')
        
        self.new_machines_tree = self.xml.get_object('new_machines_tree')
        self.machine_tree = self.xml.get_object('machinetree')
        self.users_tree = self.xml.get_object('userstree')
        self.cash_flow_tree = self.xml.get_object('cash_flow_tree')
        self.open_debts_treeview = self.xml.get_object('open_debts_treeview')
        
        self.ui_manager1 = self.xml.get_object("uimanager1")
        
        self.bntaction1 = self.xml.get_object('bntaction1')
        self.bntaction2 = self.xml.get_object('bntaction2')
        self.bntaction3 = self.xml.get_object('bntaction3')
        self.bntaction4 = self.xml.get_object('bntaction4')
        
        self.statusbar = self.xml.get_object("statusbar")
        self.columns_mnu = self.ui_manager1.get_widget(
                       '/ui/MainMenu/mnuView/coluns_mnu')
        self.tray_menu = self.xml.get_object('tray_menu')
        self.show_menu = self.xml.get_object('show_menu')
        
        self.date_daily_calendar = DateEdit.DateEdit()
        
        self.xml.get_object("daily_day_hbox").pack_start(self.date_daily_calendar)
        self.date_daily_calendar.show()
        self.daily_calendar = self.date_daily_calendar.get_internal_calendar()
        
        self.daily_calendar.connect("day-selected",
                                    self.on_cash_flow_calendar_day_selected)
        
        self.daily_calendar.connect("month-changed",
                                    self.on_cash_flow_calendar_month_changed)
        
        self.xml.get_object('machine_tgbnt').set_mode(False)
        self.xml.get_object('users_tgbnt').set_mode(False)
        self.xml.get_object('cash_flow_tgl').set_mode(False)
        self.xml.get_object('open_debts_radio_btn').set_mode(False)
        
        icon_theme = gtk.icon_theme_get_default()
        self.machine_search_entry = SearchEntry(icon_theme)
        self.user_search_entry = SearchEntry(icon_theme)
        self.cash_flow_search_entry = SearchEntry(icon_theme)
        self.open_debts_search_entry = SearchEntry(icon_theme)
        
        self.xml.get_object("find_machines_title").set_mnemonic_widget(
                                                self.machine_search_entry)
        self.xml.get_object("find_machines_label").set_mnemonic_widget(
                                                self.machine_search_entry)
        
        self.xml.get_object("find_users_title").set_mnemonic_widget(
                                                self.user_search_entry)
        self.xml.get_object("find_users_label").set_mnemonic_widget(
                                                self.user_search_entry)
        
        self.xml.get_object("cash_flow_search_title").set_mnemonic_widget(
                                                self.cash_flow_search_entry)
        self.xml.get_object("cash_flow_search_label").set_mnemonic_widget(
                                                self.cash_flow_search_entry)
        
        self.xml.get_object("title_open_debts").set_mnemonic_widget(
                                                self.open_debts_search_entry)
        self.xml.get_object("label_open_debts").set_mnemonic_widget(
                                                self.open_debts_search_entry)
        
        self.machine_search_entry.connect("terms-changed",
                                                self.on_machine_search)
        self.user_search_entry.connect("terms-changed", self.on_user_search)
        self.cash_flow_search_entry.connect("terms-changed",
                                                self.on_cash_flow_search)
        self.open_debts_search_entry.connect("terms-changed",
                                                self.on_open_debts_search)
        
        self.machine_search_entry.show()
        self.user_search_entry.show()
        self.cash_flow_search_entry.show()
        self.open_debts_search_entry.show()
        
        self.config_trees()

        self.tray = tray.Tray(_("OpenLanhouse - Server"),
                             None, "openlh-server")
        
        if self.tray.iconsuport:
            self.tray.icon.connect('popup-menu', self.tray_menu_show)
            self.tray.icon.connect('activate', self.show_hide)
        
        sel = self.gconf_client.get_int('/apps/openlh-server/ui/page_selected')
        self.set_page_selected(sel)
        
        if self.gconf_client.get_bool('/apps/openlh-server/ui/show_toolbar'):
            self.xml.get_object("show_toolbar_menu").set_active(True)
        else:
            self.xml.get_object("MainToolbar").hide()

        if self.gconf_client.get_bool('/apps/openlh-server/ui/show_status_bar'):
            self.xml.get_object("show_status_bar_menu").set_active(True)
        else:
            self.statusbar.hide()
        
        if self.gconf_client.get_bool('/apps/openlh-server/ui/maximized'):
            self.mainwindow.maximize()
        
        width = self.gconf_client.get_int('/apps/openlh-server/ui/width')
        height = self.gconf_client.get_int('/apps/openlh-server/ui/height')
        self.mainwindow.set_default_size(width, height)
        
        x = self.gconf_client.get_int('/apps/openlh-server/ui/position_x')
        y = self.gconf_client.get_int('/apps/openlh-server/ui/position_y')
        self.mainwindow.move(x, y)
        
        if self.gconf_client.get_bool('/apps/openlh-server/ui/visible'):
            self.mainwindow.show()
            self.visible = True
            self.show_menu.set_active(True)

        self.populate_trees()
        
        if self.gconf_client.get_bool('/apps/openlh-server/ui/show_side_bar'):
            self.set_view_mode(True)
        else:
            self.set_view_mode(False)
        
        self.xml.connect_signals(self)
        
        #Load Plugins
        self.daemon.load_plugins(self)
    
    def on_window_state_event(self, obj, event):
        if event.new_window_state == gtk.gdk.WINDOW_STATE_MAXIMIZED:
            self.gconf_client.set_bool('/apps/openlh-server/ui/maximized',
                                       True)
            self.statusbar.set_has_resize_grip(False)
            
        elif event.new_window_state == 0:
            self.gconf_client.set_bool('/apps/openlh-server/ui/maximized',
                                       False)
            self.statusbar.set_has_resize_grip(True)
    
    def save_window_positions(self):
        width, height = self.mainwindow.get_size()
        self.gconf_client.set_int('/apps/openlh-server/ui/width', width)
        self.gconf_client.set_int('/apps/openlh-server/ui/height', height)
        
        x, y = self.mainwindow.get_position()
        self.gconf_client.set_int('/apps/openlh-server/ui/position_x', x)
        self.gconf_client.set_int('/apps/openlh-server/ui/position_y', y)
    
    def populate_trees(self):
        
        #Populate Machines treeview
        
        message_id = self.statusbar.push(0, _('Loading machines'))
        
        for key, inst in self.instmachine_manager.machines_by_hash_id.items():
            
            icon = self.get_icon_by_machine_inst(inst)
            lst = (inst.id, icon, inst.source, inst.name, "", "", "", 0, "", 0, "")
            iter = self.machine_list_store.append(lst)
            self.machines_iters[key] = iter
        
        self.statusbar.remove(0, message_id)
        self.on_update_machines_time() #Start Loop to update times
        
        #Populate Users treeview
        message_id = self.statusbar.push(0, _('Loading users'))
        
        self.users_manager.connect('insert', self.on_new_user)
        self.users_manager.connect('delete', self.on_delete_user)
        self.users_manager.connect('update', self.on_update_user)
        self.users_manager.connect('credit_update', self.on_credit_update_user)
        
        for user in self.users_manager.get_all():
            
            iter = self.users_list_store.append((user.id, user.nick,
                                                 user.full_name,
                                                 user.email,
                                                 "%0.2f" % user.credit))
            
            self.users_iters[user.id] = iter
            
        self.statusbar.remove(0, message_id)
        
        #Populate Cash Flow
        cal = self.daily_calendar
        self.on_cash_flow_calendar_day_selected(cal)
        self.on_cash_flow_calendar_month_changed(cal)
        
        year, month, day = localtime()[0:3]
            
        self.xml.get_object("day_classic").set_value(day)
        
        self.xml.get_object("monthly_year").set_value(year)
        self.xml.get_object("year_classic").set_value(year)
        
        self.xml.get_object("monthly_combo").set_active(month -1)
        self.xml.get_object("month_classic").set_active(month -1)
        
        self.xml.get_object("monthly_combo").connect("changed",
                            self.on_cash_flow_calendar_monthly_mode_changed)
        
        self.xml.get_object("monthly_year").connect("value-changed",
                            self.on_cash_flow_calendar_monthly_mode_changed)
            
        self.cash_flow_manager.connect('insert',
                                              self.on_cash_flow_insert)
        
        #Populate OpenDebts Machine
        message_id = self.statusbar.push(0, _('Loading OpenDebts'))
        
        self.open_debts_machine_manager.connect('insert', 
                                            self.on_insert_opendebt_machine)
        self.open_debts_machine_manager.connect('delete', 
                                            self.on_delete_opendebt_machine)
        self.open_debts_machine_manager.connect('update', 
                                            self.on_update_opendebt_machine)
        
        for item in self.open_debts_machine_manager.get_all():
            if item.user:
                username = user.full_name
            else:
                username = _("Unknown user")
            
            if item.machine:
                machine_name = item.machine.name
            else:
                machine_name = _("Unknown machine")
            
            the_time = datetime.date(int(item.year), int(item.month), int(item.day))
            
            iter = self.open_debts_machine_store.append((item.id,
                                                the_time.strftime('%x'),
                                                machine_name,
                                                item.start_time, 
                                                item.end_time, 
                                                username,
                                                item.notes,
                                                "%0.2f" % item.value))
            
            self.open_debts_machine_iters[item.id] = iter
            
        self.statusbar.remove(0, message_id)
        
        #Populate Categories machine
        message_id = self.statusbar.push(0, _('Loading Machine Categories'))
        
        self.machine_category_manager.connect('insert', 
                                            self.on_insert_category_machine)
        self.machine_category_manager.connect('delete', 
                                            self.on_delete_category_machine)
        self.machine_category_manager.connect('update', 
                                            self.on_update_category_machine)
        
        tree = self.xml.get_object('machines_types_tree')
        
        self.machines_category_model = gtk.TreeStore(gobject.TYPE_PYOBJECT,
                                                     gtk.gdk.Pixbuf,
                                                     gobject.TYPE_STRING,
                                                     gobject.TYPE_STRING,
                                                     gobject.TYPE_BOOLEAN)
        
        tree.set_model(self.machines_category_model)
        
        column = gtk.TreeViewColumn()
        image_cell = gtk.CellRendererPixbuf()
        text_cell = gtk.CellRendererText()
        
        column.pack_start(image_cell, expand=False)
        column.pack_start(text_cell, expand=True)
        
        column.add_attribute(image_cell, 'pixbuf', 1)
        column.add_attribute(text_cell, 'markup', 2)
        column.add_attribute(image_cell, "visible", 4)
        
        tree.append_column(column)
        
        self.populate_category_machine(0, _("All Machines"))
        
        #populate
        for i in self.machine_category_manager.get_all():
            self.populate_category_machine(i.id, i.name)
        
        self.statusbar.remove(0, message_id)
        
        #Populate Categories Open Debts
        tree = self.xml.get_object('open_debts_types_tree')
        
        model = gtk.ListStore(gobject.TYPE_PYOBJECT,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING)
        
        tree.set_model(model)
        
        column = gtk.TreeViewColumn()
        text_cell = gtk.CellRendererText()
        column.pack_start(text_cell, expand=True)
        column.add_attribute(text_cell, 'markup', 1)
        
        tree.append_column(column)
        
        model.append((0, _("<b>Machine usage</b>"), _("fill me")))
        model.append((1, _("<b>Other</b>"), _("fill me")))
        
        self.set_open_debts_selected_page()
        
        #Set Sensitive True
        self.xml.get_object('MainMenu').set_sensitive(True)
        self.xml.get_object('MainToolbar').set_sensitive(True)
        self.xml.get_object('notebook').set_sensitive(True)
    
    def on_newmachinemnu_activate(self, obj):
        dlg = dialogs.AlertAddMachine(Parent=self.mainwindow)
        
        if dlg.run():
            dlg = dialogs.AddMachine(Parent=self.mainwindow, Manager=self)
            data = dlg.run(set_hash_sensitive=True)
            if data:
                self.instmachine_manager.allow_machine(data['hash_id'],
                                                       data, None)
    
    def on_new_user_menuitem_activate(self, obj):
        price_per_hour = self.gconf_client.get_float(
                                '/apps/openlh-server/price_per_hour')
        
        dlg = dialogs.adduser(users_manager=self.users_manager,
                              cash_flow_manager=self.cash_flow_manager,
                              price_per_hour=price_per_hour,
                              Parent=self.mainwindow)
        
        dlg.run()
    
    def on_ticket_menuitem_activate(self, obj):
        price_per_hour = self.gconf_client.get_float(
                                '/apps/openlh-server/price_per_hour')
        
        dlg = dialogs.new_ticket(Parent=self.mainwindow)
        
        dlg.run()
    
    def new_clicked(self, obj):
        
        if self.selpage == 0:
            dlg = dialogs.AlertAddMachine(Parent=self.mainwindow)
            if dlg.run():
                dlg = dialogs.AddMachine(Parent=self.mainwindow, Manager=self)
                data = dlg.run(set_hash_sensitive=True)
                if data:
                    self.instmachine_manager.allow_machine(data['hash_id'],
                                                       data, None)
        
        elif self.selpage == 1:
            price_per_hour = self.gconf_client.get_float(
                                    '/apps/openlh-server/price_per_hour')
            
            dlg = dialogs.adduser(users_manager=self.users_manager,
                                  cash_flow_manager=self.cash_flow_manager,
                                  price_per_hour=price_per_hour,
                                  Parent=self.mainwindow)
            
            dlg.run()
        
        elif self.selpage == 2:
            dlg = dialogs.NewCashFlowItem(users_manager=self.users_manager,
                                  Parent=self.mainwindow)
            
            data = dlg.run()
            
            if not data:
                return
            
            #Insert Entry in Cash Flow
            lctime = localtime()
            current_hour = "%0.2d:%0.2d:%0.2d" % lctime[3:6]
        
            citem = CashFlowItem()
            
            if data['type']:
                citem.type = CASH_FLOW_CUSTOM_TYPE_OUT
            else:
                citem.type = CASH_FLOW_CUSTOM_TYPE_IN
            
            citem.value = data['value']
            citem.notes = data['notes']
            citem.year = lctime[0]
            citem.month = lctime[1]
            citem.day = lctime[2]
            citem.hour = current_hour
            
            if 'user_id' in data:
                citem.user_id = data['user_id']
            
            self.cash_flow_manager.insert(citem)
        
    def new_machine(self, data):
        print data
        
    def prefs_clicked(self, obj):
        self.set_sensitive(False)
        dlg= prefs.Prefs(Parent=self.mainwindow)
        dlg.prefs.run()
        dlg.prefs.hide()
        self.reload_configs()
        self.set_sensitive(True)
        
    def reload_configs(self):
        self.daemon.reload_configs()
    
    def edit_clicked(self, obj):
        model, iteration = self.get_selects(self.seltree)
        
        if self.selpage == 0 and iteration:
            machine_id = int(model.get_value(iteration, 0))
            assert self.instmachine_manager.machines_by_id[machine_id]
            machine_inst = self.instmachine_manager.machines_by_id[machine_id]
            
            dlg = dialogs.AddMachine(Parent=self.mainwindow, Manager=self)
            dlg.dialog.set_title(_("Edit Machine - OpenLanhouse"))
            data = dlg.run({'hash_id': machine_inst.hash_id,
                            'name': machine_inst.name,
                            'description': machine_inst.description,
                            'category_id': machine_inst.category_id
                            }
                          )
            
            if data:
                self.instmachine_manager.update(machine_inst, data)
            
        elif self.selpage == 1 and iteration:
            id = int(model.get_value(iteration, 0))
            user = self.users_manager.get_all().filter_by(id=id).one()
            
            app = dialogs.user_edit(users_manager=self.users_manager,
                                     Parent=self.mainwindow)
            
            app.run(user)
    
    def properties_clicked(self, obj):
        model, iteration = self.get_selects(self.seltree)
        
        if self.selpage == 0 and iteration:
            machine_id = int(model.get_value(iteration, 0))
            assert self.instmachine_manager.machines_by_id[machine_id]
            machine_inst = self.instmachine_manager.machines_by_id[machine_id]
            last_user_id = self.machine_manager.get_last_user_id(machine_inst.id)
            
            last_user = None
            if last_user_id:
                last_user = self.users_manager.get_full_name(last_user_id)
            
            dlg = dialogs.machine_info(self.mainwindow)
            dlg.run(machine_inst, last_user)
        
        if self.selpage == 1 and iteration:
            
            user_id = int(model.get_value(iteration, 0))
            
            user = self.users_manager.get_all().filter_by(id=user_id).one()
            credit = self.users_manager.get_credit(User.id, user.id)
            last_machine = self.machine_manager.get_name(user.last_machine_id)
            currency = self.gconf_client.get_string('/apps/openlh-server/currency')
            
            if user:
                dlg = dialogs.user_info(self.users_manager, self.mainwindow)
                dlg.run(currency, user, credit, last_machine)
        
    def del_clicked(self, obj):
        model, iteration = self.get_selects(self.seltree)
        
        if self.selpage == 0 and iteration:
            machine_id = int(model.get_value(iteration, 0))
            assert self.instmachine_manager.machines_by_id[machine_id]
            machine_inst = self.instmachine_manager.machines_by_id[machine_id]
        
            if machine_inst.status == 2:
                dialogs.ok_only(_("<b><big>Unable to delete machine</big></b>\n\n"
                                "This machine is in use"),
                                Parent=self.mainwindow,
                                ICON=gtk.MESSAGE_ERROR)
                return
            
            d = dialogs.delete(_("<b><big>Are you sure you want to "
                                 "permanently delete '%s'?</big></b>\n\n"
                                 "if you delete this machine, "
                                 "it will be permanently lost") % machine_inst.name,
                               Parent=self.mainwindow)
            
            if d.response:
                self.instmachine_manager.delete_machine(machine_inst)
            
        elif self.selpage == 1 and iteration:
            id = int(model.get_value(iteration, 0))
            user = self.users_manager.get_all().filter_by(id=id).one()
            
            #TODO: assert credit == 0
            d = dialogs.delete(_("<b><big>Are you sure you want to "
                                 "permanently delete '%s'?</big></b>\n\n"
                                 "if you delete this user, "
                                 "it will be permanently lost") % user.full_name,
                               Parent=self.mainwindow)
            
            if d.response:
                #Remove Avatar File
                if user_has_avatar(user.id):
                    try:
                        os_remove(get_user_avatar_path(user.id))
                    except Exception , e:
                        print str(e)
                
                self.users_manager.delete(user)
    
    def block_machine_clicked(self, obj):
        model, iteration = self.get_selects(self.machine_tree)
        
        if not iteration:
            return
        
        machine_id = int(model.get_value(iteration, 0))
        assert self.instmachine_manager.machines_by_id[machine_id]
        machine_inst = self.instmachine_manager.machines_by_id[machine_id]
        
        if machine_inst.status == 0:
            dialogs.ok_only(_("<b><big>Unable to block machine</big></b>\n\n"
                              "This machine is not available"),
                            Parent=self.mainwindow,
                            ICON=gtk.MESSAGE_ERROR)
            return
        
        elif machine_inst.status == 1:
            dialogs.ok_only(_("<b><big>Unable to block machine</big></b>\n\n"
                              "This machine already blocked"),
                            Parent=self.mainwindow,
                            ICON=gtk.MESSAGE_ERROR)
            return
        
        dlg = dialogs.block_machine(machine_name=machine_inst.name,
                                    Parent=self.mainwindow)
        block, after, action = dlg.run()
        
        if block:
            self.instmachine_manager.block(machine_inst,
                                       after,
                                       action
                                      )
    
    def unblock_machine_clicked(self, obj):
        model, iteration = self.get_selects(self.machine_tree)
        
        if not iteration:
            return
        
        machine_id = int(model.get_value(iteration, 0))
        assert self.instmachine_manager.machines_by_id[machine_id]
        machine_inst = self.instmachine_manager.machines_by_id[machine_id]
        
        if machine_inst.status == 0:
            dialogs.ok_only(_("<b><big>Unable to unblock machine</big></b>\n\n"
                              "This machine is not available"),
                            Parent=self.mainwindow,
                            ICON=gtk.MESSAGE_ERROR)
            return
        elif machine_inst.status == 2:
            dialogs.ok_only(_("<b><big>Unable to unblock machine</big></b>\n\n"
                              "This machine already in use"),
                            Parent=self.mainwindow,
                            ICON=gtk.MESSAGE_ERROR)
            return
        
        price_per_hour = self.gconf_client.get_float(
                    '/apps/openlh-server/price_per_hour')
        
        currency = self.gconf_client.get_string(
                    '/apps/openlh-server/currency')
        
        dlg = dialogs.unblock_machine(price_per_hour=price_per_hour,
                                      currency=currency,
                                      users_manager = self.users_manager,
                                      Parent=self.mainwindow)
        data = dlg.run()
        
        del dlg
        
        if data:
            self.instmachine_manager.unblock(machine_inst,
                                         data['registred'],
                                         data['limited'],
                                         data['user_id'],
                                         data['time']
                                        )
    
    def on_view_history_machine(self, obj):
        model, iteration = self.get_selects(self.machine_tree)
        
        if not iteration:
            return
        
        machine_id = int(model.get_value(iteration, 0))
        assert self.instmachine_manager.machines_by_id[machine_id]
        machine_inst = self.instmachine_manager.machines_by_id[machine_id]
        
        dlg = dialogs.machine_history(self.history_manager,
                                      Parent=self.mainwindow)
        dlg.run(machine_inst)
    
    def on_view_history_user(self, obj):
        
        model, iteration = self.get_selects(self.seltree)
        
        if not iteration:
            return
        
        user_id = int(model.get_value(iteration, treeview.USERS_CEL_ID))
        user_name = model.get_value(iteration, treeview.USERS_CEL_NAME)
        
        dlg = dialogs.user_history(self.history_manager,
                                   Parent=self.mainwindow)
        dlg.run(user_id, user_name)
    
    #Add/Remove Time
    def on_add_time_clicked(self, obj):
        model, iteration = self.get_selects(self.machine_tree)
        
        if not iteration:
            return
        
        machine_id = int(model.get_value(iteration, 0))
        assert self.instmachine_manager.machines_by_id[machine_id]
        machine_inst = self.instmachine_manager.machines_by_id[machine_id]
        
        if machine_inst.status != 2:
            dialogs.ok_only(_("<b><big>Unable to add time</big></b>\n\n"
                              "This machine is not in use."),
                            Parent=self.mainwindow,
                            ICON=gtk.MESSAGE_ERROR)
            return
        
        
        if not machine_inst.limited:
            dialogs.ok_only(_("<b><big>Unable to add time</big></b>\n\n"
                              "This machine is not used in limited mode."),
                            Parent=self.mainwindow,
                            ICON=gtk.MESSAGE_ERROR)
            return
        
        price_per_hour = self.gconf_client.get_float(
                        '/apps/openlh-server/price_per_hour')
        
        dlg = dialogs.add_time(price_per_hour, Parent=self.mainwindow)
        a_time = dlg.run()
        
        if a_time:
            hour, minutes, seconds = a_time
            a_time = (hour, minutes)
            self.instmachine_manager.add_time(machine_inst, a_time)
    
    def on_remove_time_clicked(self, obj):
        model, iteration = self.get_selects(self.machine_tree)
        
        if not iteration:
            return
        
        machine_id = int(model.get_value(iteration, 0))
        assert self.instmachine_manager.machines_by_id[machine_id]
        machine_inst = self.instmachine_manager.machines_by_id[machine_id]
        
        if machine_inst.status != 2:
            dialogs.ok_only(_("<b><big>Unable to remove time</big></b>\n\n"
                              "This machine is not in use."),
                            Parent=self.mainwindow,
                            ICON=gtk.MESSAGE_ERROR)
            return
        
        if not machine_inst.limited:
            dialogs.ok_only(_("<b><big>Unable to remove time</big></b>\n\n"
                              "This machine is not used in limited mode."),
                            Parent=self.mainwindow,
                            ICON=gtk.MESSAGE_ERROR)
            return
        
        price_per_hour = self.gconf_client.get_float(
                        '/apps/openlh-server/price_per_hour')
        
        dlg = dialogs.remove_time(price_per_hour, Parent=self.mainwindow)
        a_time = dlg.run()
        
        if a_time:
            hour, minutes, seconds = a_time
            a_time = (hour, minutes)
            self.instmachine_manager.remove_time(machine_inst, a_time)
            
    def on_machine_search(self, obj, text):
        self.machine_search_text = text
        self.machine_filtered.refilter()
        
    def on_user_search(self, obj, text):
        self.user_search_text = text
        self.users_filtered.refilter()
    
    def on_cash_flow_search(self, obj, text):
        self.cash_flow_search_text = text
        self.cash_flow_filtered.refilter()
    
    def on_open_debts_search(self, obj, text):
        print obj, text
    
    def on_machine_visible_cb(self, model, iter):
        
        machine_id = model.get_value(iter, treeview.MACHINE_CEL_ID)
        
        if machine_id and not(self.check_machine_filter(int(machine_id))):
            return False
        
        if self.machine_search_text == "":
            return True
        
        t = False
        for col in treeview.MACHINE_SEARCHABLE_COLS:
            x = model.get_value(iter, col)
            if x and self.machine_search_text in x:
                t = True
                break
        
        return t
    
    def on_user_visible_cb(self, model, iter):
        if self.user_search_text == "":
            return True
        
        t = False
        for col in treeview.USER_SEARCHABLE_COLS:
            x = model.get_value(iter, col)
            if x and self.user_search_text in x:
                t = True
                break
        
        return t
    
    def on_cash_flow_visible_cb(self, model, iter):
        if self.cash_flow_search_text  == "":
            return True
        
        t = False
        for col in treeview.CASH_FLOW_SEARCHABLE_COLS:
            x = model.get_value(iter, col)
            if x and self.cash_flow_search_text in x:
                t = True
                break
        
        return t
    
    def on_open_debts_machine_visible_cb(self, model, iter):
        return True#Fix-me
        
    def on_open_debts_other_visible_cb(self, model, iter):
        return True#Fix-me
    
    def add_credit_clicked(self, obj):
        model, iteration = self.get_selects(self.seltree)
        
        if not iteration:
            return
        
        user_id = int(model.get_value(iteration, 0))
        
        price_per_hour = self.gconf_client.get_float(
                        '/apps/openlh-server/price_per_hour')
        
        dlg = dialogs.AddCredit(price_per_hour,
                                Parent=self.mainwindow)
            
        credit, notes = dlg.run()

        if not credit:
            return
        
        current_credit = self.users_manager.get_credit(User.id, user_id)
        current_credit += credit
        self.users_manager.update_credit(user_id, current_credit)
        
        #Insert Entry in Cash Flow
        lctime = localtime()
        current_hour = "%0.2d:%0.2d:%0.2d" % lctime[3:6]
        
        citem = CashFlowItem()
        citem.type = CASH_FLOW_TYPE_CREDIT_IN
        citem.value = credit
        citem.user_id = user_id
        citem.notes = notes
        citem.year = lctime[0]
        citem.month = lctime[1]
        citem.day = lctime[2]
        citem.hour = current_hour
        
        self.cash_flow_manager.insert(citem)
    
    def del_credit_clicked(self, obj):
        model, iteration = self.get_selects(self.seltree)
        
        if not iteration:
            return
        
        user_id = int(model.get_value(iteration, 0))
        
        price_per_hour = self.gconf_client.get_float(
                                '/apps/openlh-server/price_per_hour')
        
        currency = self.gconf_client.get_string(
                                      '/apps/openlh-server/currency')
        
        current_credit = self.users_manager.get_credit(User.id, user_id)
        
        dlg = dialogs.RemoveCredit(self.users_manager, 
                                   currency, user_id, current_credit,
                                   Parent=self.mainwindow)
        
        credit_to_remove, notes = dlg.run()

        if not credit_to_remove:
            return
        
        current_credit -= credit_to_remove
        self.users_manager.update_credit(user_id, current_credit)
        
        #Insert Entry in Cash Flow
        lctime = localtime()
        current_hour = "%0.2d:%0.2d:%0.2d" % lctime[3:6]
        
        citem = CashFlowItem()
        citem.type = CASH_FLOW_TYPE_CREDIT_OUT
        citem.value = credit_to_remove
        citem.user_id = user_id
        citem.notes = notes
        citem.year = lctime[0]
        citem.month = lctime[1]
        citem.day = lctime[2]
        citem.hour = current_hour
        
        self.cash_flow_manager.insert(citem)
    
    def change_password_clicked(self, obj):
        model, iteration = self.get_selects(self.seltree)
        
        if not iteration:
            return None
        
        user_id = int(model.get_value(iteration, 0))
        
        dlg = dialogs.change_password(Parent=self.mainwindow)
        password = dlg.run()
        
        if password:
            self.users_manager.change_password(user_id, md5_cripto(password))
    
    def new_machine_by_mnu(self, obj):
        print "New Machine"
    
    def new_user_by_mnu(self, obj):
        print 'new_user_by_mnu'
        """" #FIX_ME
        price_per_hour = self.gconf_client.get_float(
                              '/apps/openlh-server/price_per_hour')
        
        app = dialogs.adduser(database=self.database_user,
                              cash_flow_manager=self.cash_flow_manager,
                              price_per_hour=price_per_hour,
                              Parent=self.mainwindow)
        app.run()
        """
    def new_ticket_by_mnu(self, obj):
        print 'new_ticket_by_mnu'
    
    def on_bntaction1_clicked(self, obj):
        if self.selpage == 0:
            self.unblock_machine_clicked(obj)
            
        elif self.selpage == 1:
            self.add_credit_clicked(obj)
        
        elif self.selpage == 3:
            pagenum = self.xml.get_object(
                    "open_debts_notebook").get_current_page()
            
            if pagenum == 0:
                self.on_paid_open_debts_machine(obj)
            elif pagenum == 1:
                self.on_paid_open_debts_other(obj)
        
    def on_bntaction2_clicked(self, obj):
        if self.selpage == 0:
            self.block_machine_clicked(obj)
        elif self.selpage == 1:
            self.del_credit_clicked(obj)
    
    def on_bntaction3_clicked(self, obj):
        if self.selpage == 0:
            self.on_add_time_clicked(obj)
    
    def on_bntaction4_clicked(self, obj):
        if self.selpage == 0:
            self.on_remove_time_clicked(obj)
    
    #####################################
    ### NOTEBOOK FUNCTIONS
    #####################################
    
    def set_page_selected(self, num):
        
        self.notebook_interative = False
        
        if not num in range(4):
            num = 0
        
        self.selpage = num
        
        self.xml.get_object("remtime_mnit").set_property("visible", num==0)
        self.xml.get_object("addtime_mnit").set_property("visible", num==0)
        self.xml.get_object("change_pass_mnu").set_property("visible", num==1)
        self.xml.get_object("paid_menuitem").set_property("visible", num==3)
        
        if num == 0:
            t = (self.machine_tree, self.machine_treemnu)
            
            for path in ('menuEdit/insertmnu', 'menuEdit/removecreditmnu'):
                self.ui_manager1.get_widget("/ui/MainMenu/%s" % path).hide()
                
            for path in ('menuEdit/mnuLib', 'menuEdit/mnuBlock', 
                         'menuEdit/view_history_menuitem'):
                self.ui_manager1.get_widget("/ui/MainMenu/%s" % path).show()
            
            self.bntaction1.set_sensitive(True)
            self.bntaction2.set_sensitive(True)
            self.bntaction3.set_sensitive(True)
            self.bntaction4.set_sensitive(True)
            
            self.xml.get_object("toolbar_separator2").show()
            
            self.bntaction1.set_label(_('_Unblock'))
            self.bntaction1.set_stock_id(gtk.STOCK_NO)
            
            self.bntaction2.set_label(_('_Block'))
            self.bntaction2.set_stock_id(gtk.STOCK_YES)
            
            self.bntaction3.set_label(_('_Add Time'))
            self.bntaction3.set_stock_id(gtk.STOCK_ADD)
            
            self.bntaction4.set_label(_('_Remove Time'))
            self.bntaction4.set_stock_id(gtk.STOCK_REMOVE)
            
            tgbnt = self.xml.get_object('machine_tgbnt')
            
            if not tgbnt.get_active():
                tgbnt.set_active(True)
            
            if self.cash_flow_status_msg_id:
                self.statusbar.remove(0, self.cash_flow_status_msg_id)
            
        elif num == 1:
            t = (self.users_tree, self.users_treemnu)
            
            for path in ('menuEdit/insertmnu', 'menuEdit/removecreditmnu',
                         'menuEdit/view_history_menuitem'):
                self.ui_manager1.get_widget("/ui/MainMenu/%s" % path).show()
                
            for path in ('menuEdit/mnuLib', 'menuEdit/mnuBlock'):
                self.ui_manager1.get_widget("/ui/MainMenu/%s" % path).hide()
            
            self.bntaction1.set_sensitive(True)
            self.bntaction2.set_sensitive(True)
            self.bntaction3.set_sensitive(False)
            self.bntaction4.set_sensitive(False)
            
            self.bntaction1.set_label(_('_Add Credit'))
            self.bntaction1.set_stock_id(gtk.STOCK_ADD)
            
            self.bntaction2.set_label(_('_Remove Credit'))
            self.bntaction2.set_stock_id(gtk.STOCK_REMOVE)
            
            self.xml.get_object("toolbar_separator1").show()
            self.xml.get_object("toolbar_separator2").hide()
            
            self.bntaction3.set_label('')
            self.bntaction3.set_stock_id(None)
            
            self.bntaction4.set_label('')
            self.bntaction4.set_stock_id(None)
            
            tgbnt = self.xml.get_object('users_tgbnt')
            if not tgbnt.get_active():
                tgbnt.set_active(True)
            
            if self.cash_flow_status_msg_id:
                self.statusbar.remove(0, self.cash_flow_status_msg_id)
        
        elif num == 2:
            t = (self.cash_flow_tree, self.cash_flow_treemnu)
            
            self.bntaction1.set_sensitive(False)
            self.bntaction2.set_sensitive(False)
            self.bntaction3.set_sensitive(False)
            self.bntaction4.set_sensitive(False)
            
            self.xml.get_object("toolbar_separator1").hide()
            self.xml.get_object("toolbar_separator2").hide()
            
            self.bntaction1.set_label('')
            self.bntaction1.set_stock_id(None)
            
            self.bntaction2.set_label('')
            self.bntaction2.set_stock_id(None)
            
            self.bntaction3.set_label('')
            self.bntaction3.set_stock_id(None)
            
            self.bntaction4.set_label('')
            self.bntaction4.set_stock_id(None)
            
            for path in ('menuEdit/insertmnu', 'menuEdit/removecreditmnu',
                         'menuEdit/mnuLib', 'menuEdit/mnuBlock',
                         'menuEdit/view_history_menuitem'):
                self.ui_manager1.get_widget("/ui/MainMenu/%s" % path).hide()
            
            tgbnt = self.xml.get_object('cash_flow_tgl')
            if not tgbnt.get_active():
                tgbnt.set_active(True)
        
        elif num == 3:
            t = (self.open_debts_treeview, None)
            self.bntaction1.set_sensitive(True)
            self.bntaction2.set_sensitive(False)
            self.bntaction3.set_sensitive(False)
            self.bntaction4.set_sensitive(False)
            
            self.xml.get_object("toolbar_separator1").show()
            self.xml.get_object("toolbar_separator2").hide()
            
            self.bntaction1.set_label(_('_Paid'))
            self.bntaction1.set_stock_id(gtk.STOCK_APPLY)
            
            self.bntaction2.set_label('')
            self.bntaction2.set_stock_id(None)
            
            self.bntaction3.set_label('')
            self.bntaction3.set_stock_id(None)
            
            self.bntaction4.set_label('')
            self.bntaction4.set_stock_id(None)
            
            for path in ('menuEdit/insertmnu', 'menuEdit/removecreditmnu',
                         'menuEdit/mnuLib', 'menuEdit/mnuBlock',
                         'menuEdit/view_history_menuitem'):
                self.ui_manager1.get_widget("/ui/MainMenu/%s" % path).hide()
            
            tgbnt = self.xml.get_object('open_debts_radio_btn')
            if not tgbnt.get_active():
                tgbnt.set_active(True)
            
            if self.cash_flow_status_msg_id:
                self.statusbar.remove(0, self.cash_flow_status_msg_id)
            
            open_debts_sel_page = self.xml.get_object(
                    "open_debts_notebook").get_current_page()
            
            if open_debts_sel_page == 0:
                seltreemnu = self.open_debts_machine_treemnu
            elif open_debts_sel_page == 1:
                seltreemnu = self.open_debts_other_treemnu
            
            self.columns_mnu.remove_submenu()
            self.columns_mnu.set_submenu(seltreemnu)
            seltreemnu.show()
            
        (self.seltree, self.seltreemnu) = t
        
        if self.seltreemnu:
            self.columns_mnu.remove_submenu()
            self.columns_mnu.set_submenu(self.seltreemnu)
            self.seltreemnu.show()
        
        for widget in 'notebook', 'left_notebook':
            self.xml.get_object(widget).set_current_page(num)
        
        self.update_status_label_for_cash_flow()
        
        self.gconf_client.set_int('/apps/openlh-server/ui/page_selected', num)
        self.notebook_interative = True
    
    def config_trees(self):
        
        self.machine_col = treeview.machine()
        self.users_col = treeview.users()
        self.cash_flow_col = treeview.cash_flow()
        self.open_debts_machine_col = treeview.open_debts_machine()
        self.open_debts_other_col = treeview.open_debts_other()
        
        self.machine_mnu = self.xml.get_object("machines_tree_menu")
        self.users_mnu = self.xml.get_object("users_tree_menu")

        for column in self.machine_col.get_columns():
            self.machine_tree.append_column(column)
        
        for column in self.users_col.get_columns():
            self.users_tree.append_column(column)
        
        for column in self.cash_flow_col.get_columns():
            self.cash_flow_tree.append_column(column)
        
        for column in self.open_debts_machine_col.get_columns():
            self.xml.get_object(
                    "open_debts_machine_treeview").append_column(column)
        
        for column in self.open_debts_other_col.get_columns():
            self.xml.get_object(
                    "open_debts_other_treeview").append_column(column)
        
        self.machine_list_store = self.machine_col.get_list_store()
        self.users_list_store = self.users_col.get_list_store()
        self.cash_flow_list_store = self.cash_flow_col.get_list_store()
        self.open_debts_machine_store = self.open_debts_machine_col.get_list_store()
        self.open_debts_other_store = self.open_debts_other_col.get_list_store()
        
        self.machine_filtered = self.machine_col.get_filter()
        self.users_filtered = self.users_col.get_filter()
        self.cash_flow_filtered = self.cash_flow_col.get_filter()
        self.open_debts_machine_filtered = self.open_debts_machine_col.get_filter()
        self.open_debts_other_filtered = self.open_debts_other_col.get_filter()
        
        self.machine_filtered.set_visible_func(self.on_machine_visible_cb)
        self.users_filtered.set_visible_func(self.on_user_visible_cb)
        self.cash_flow_filtered.set_visible_func(self.on_cash_flow_visible_cb)
        self.open_debts_machine_filtered.set_visible_func(
                                        self.on_open_debts_machine_visible_cb)
        self.open_debts_other_filtered.set_visible_func(
                                        self.on_open_debts_other_visible_cb)
        
        self.machine_sorted = gtk.TreeModelSort(self.machine_filtered)
        self.users_sorted = gtk.TreeModelSort(self.users_filtered)
        self.cash_flow_sorted = gtk.TreeModelSort(self.cash_flow_filtered)
        self.open_debts_machine_sorted = gtk.TreeModelSort(
                                        self.open_debts_machine_filtered)
        self.open_debts_other_sorted = gtk.TreeModelSort(
                                        self.open_debts_other_filtered)
        
        self.machine_sorted.set_sort_func(treeview.MACHINE_CEL_PIXMAP,
                                    self.on_machine_treeview_status_sort,
                                    treeview.MACHINE_CEL_PIXMAP)
        
        self.users_sorted.set_sort_func(treeview.USERS_CEL_CREDIT,
                                    self.on_user_treeview_credit_sort,
                                    treeview.USERS_CEL_CREDIT)
        
        self.cash_flow_sorted.set_sort_func(treeview.CASH_FLOW_CEL_VALUE,
                                    self.on_user_treeview_credit_sort,
                                    treeview.CASH_FLOW_CEL_VALUE)
        
        self.machine_treemnu = self.machine_col.treemnu
        self.users_treemnu = self.users_col.treemnu
        self.cash_flow_treemnu = self.cash_flow_col.treemnu
        self.open_debts_machine_treemnu = self.open_debts_machine_col.treemnu
        self.open_debts_other_treemnu = self.open_debts_other_col.treemnu

        self.machine_tree.set_model(self.machine_sorted)
        self.users_tree.set_model(self.users_sorted)
        self.cash_flow_tree.set_model(self.cash_flow_sorted)
        
        self.xml.get_object("open_debts_machine_treeview").set_model(
                                        self.open_debts_machine_sorted)
        self.xml.get_object("open_debts_other_treeview").set_model(
                                        self.open_debts_other_sorted)
        
        self.machine_tree.realize()
        self.users_tree.realize()
        self.cash_flow_tree.realize()
        self.xml.get_object("open_debts_machine_treeview").realize()
        self.xml.get_object("open_debts_other_treeview").realize()
        
        self.machine_tree.columns_autosize()
        self.users_tree.columns_autosize()
        self.cash_flow_tree.columns_autosize()
        
        self.new_machines_detect_list_store = gtk.ListStore(
                                                 gobject.TYPE_STRING,
                                                 gobject.TYPE_STRING)
        
        column = gtk.TreeViewColumn("", gtk.CellRendererText(), markup=0)
        self.new_machines_tree.append_column(column)
        column = gtk.TreeViewColumn("", gtk.CellRendererText(), markup=1)
        self.new_machines_tree.append_column(column)
        column.set_property('visible', False)
        self.new_machines_tree.set_model(self.new_machines_detect_list_store)
    
    def on_machine_treeview_status_sort(self, model, iter1, iter2, column_id):
        pix_a = model.get_value(iter1, column_id)
        pix_b = model.get_value(iter2, column_id)
        print pix_a,pix_b
        return -1
    
    def on_user_treeview_credit_sort(self, model, iter1, iter2, column_id):
        try:
            a = float(model.get_value(iter1, column_id))
        except:
            a = None
        
        try:
            b = float(model.get_value(iter2, column_id))
        except:
            b = None
        
        return cmp(a, b)

    def get_selects(self, treeview):
        selection = treeview.get_selection()
        rows = selection.get_selected_rows()
        model, iteration = selection.get_selected()
        
        return model, iteration
    
    def tree_activate(self, obj, *args):
        self.edit_clicked(obj)
        
    def tree_press_event(self, widget, event):
        
        if event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS:
            path = self.seltree.get_path_at_pos(int(event.x), int(event.y))
            selection = self.seltree.get_selection()
            
            if not path:
                return
            
            rows = selection.get_selected_rows()
            
            if path[0] not in rows[0]:
                selection.unselect_all()
                selection.select_path(path[0])
                
            model, iteration = self.get_selects(self.seltree)
            
            if self.selpage == 0 and iteration:
                self.machine_mnu.popup(None, None, None, event.button, event.get_time())
            
            if self.selpage == 1 and iteration:
                self.users_mnu.popup(None, None, None, event.button, event.get_time())
    
    def get_icon_by_machine_inst(self, machineinst):
        if machineinst.status == 0:
            return self.halt_icon
        elif machineinst.status == 1:
            return self.available_icon
        elif machineinst.status == 2:
            return self.busy_icon
    
    def populate_category_machine(self, id, name):
        tree = self.xml.get_object('machines_types_tree')
        model = tree.get_model()
        
        iter = model.append(None, ((id, None), None,
                            "<b>%s</b>" % name,
                            None, False))
        
        self.category_machines_iters[id] = iter
        
        model.append(iter, ((id, MACHINE_STATUS_AVAIL),
                            self.status_icons.get_icon("available", 16, 16),
                            _("Available"),
                            _("Available machines"),
                            True))
        
        model.append(iter, ((id, MACHINE_STATUS_BUSY),
                            self.status_icons.get_icon("busy", 16, 16),
                            _("Busy"),
                            _("Busy machines"),
                            True))
        
        model.append(iter, ((id, MACHINE_STATUS_OFFLINE),
                            self.status_icons.get_icon("halt", 16, 16),
                            _("Unavailable"),
                            _("Unavailable machines"),
                            True))
        
        tree.expand_all()
    
    def tray_menu_show(self, obj, button, event):
        self.tray_menu.popup(None, None, None, button, event)
        
    def show_hide(self, obj):
        if obj == self.show_menu:
            if self.visible != obj.get_active():
                if self.visible:
                    self.visible = False
                    self.mainwindow.hide()
                else:
                    self.visible = True
                    self.mainwindow.show()
                
                self.gconf_client.set_bool('/apps/openlh-server/ui/visible',
                                           self.visible)
        else:
            if self.visible:
                self.visible = False
                self.show_menu.set_active(False)
                self.mainwindow.hide()
            else:
                self.visible = True
                self.show_menu.set_active(True)
                self.mainwindow.show()
                
            self.gconf_client.set_bool('/apps/openlh-server/ui/visible',
                                       self.visible)
    
    def delete_event(self, *args):
        
        self.set_sensitive(False)
        
        if self.visible:
            dlg = dialogs.exit(_('<big><b>Are you sure you want to quit?'
                                 '</b></big>'),
                               Parent=self.mainwindow)
        else:
            dlg = dialogs.exit(_('<big><b>Are you sure you want to quit?'
                                 '</b></big>'))
        
        if dlg.response == gtk.RESPONSE_YES:
            self.save_window_positions()
            gtk.main_quit()
            return False
        
        else:
            self.set_sensitive(True)
            
            if dlg.response == 2: #Miminize Action
                self.show_hide(None)
            
            return True
    
    def about_clicked(self, obj):
        
        self.set_sensitive(False)
        
        if self.visible:
            dialogs.about(self.logo, self.mainwindow)
        else:
            dialogs.about(self.logo)
        
        self.set_sensitive(True)
    
    def set_sensitive(self, status):
        
        self.xml.get_object('mainvbox').set_sensitive(status)
    
    def on_new_user(self, obj, user):
        
        iter = self.users_list_store.append((user.id, user.nick,
                                             user.full_name,
                                             user.email,
                                             "%0.2f" % user.credit))
        
        self.users_iters[user.id] = iter

    def on_delete_user(self, obj, user_id):
        user_iter = self.users_iters.pop(user_id)
        self.users_list_store.remove(user_iter)
        
    def on_update_user(self, obj, user):
        #Find Iter:
        user_id = user.id
        user_iter = self.users_iters[user_id]
        credit = self.users_manager.get_credit(User.id, user_id)
        
        #update treeview:
        self.users_list_store.set(user_iter,
                                  treeview.USERS_CEL_NICK, user.nick,
                                  treeview.USERS_CEL_NAME, user.full_name,
                                  treeview.USERS_CEL_EMAIL, user.email,
                                  treeview.USERS_CEL_CREDIT,
                                  "%0.2f" % credit)
    
    def on_credit_update_user(self, obj, user_id, value):
        user_iter = self.users_iters[user_id]
        self.users_list_store.set(user_iter,
                                  treeview.USERS_CEL_CREDIT,
                                  "%0.2f" % value)
    
    #OpenDebts Machine
    def on_insert_opendebt_machine(self, obj, item):
        if item.user:
            username = user.full_name
        else:
            username = _("Unknown user")
        
        if item.machine:
            machine_name = item.machine.name
        else:
            machine_name = _("Unknown machine")
        
        the_time = datetime.date(int(item.year), int(item.month), int(item.day))
        
        iter = self.open_debts_machine_store.append((item.id,
                                                the_time.strftime('%x'),
                                                machine_name,
                                                item.start_time, 
                                                item.end_time, 
                                                username,
                                                item.notes,
                                                "%0.2f" % item.value))
            
        self.open_debts_machine_iters[item.id] = iter
        
    def on_delete_opendebt_machine(self, obj, id):
        iter = self.open_debts_machine_iters.pop(id)
        self.open_debts_machine_store.remove(iter)
        
    def on_update_opendebt_machine(self, obj, item):
        print obj, item
    
    #Machine's Detect
    def update_new_machines_state(self):
        if len(self.machine_auth_pending) != 0:
            t = self.xml.get_object("new_machine_alert_button")
            t.show()
            t.set_active(True)
        else:
            t = self.xml.get_object("new_machine_alert_button")
            t.set_active(False)
            t.hide()
            
    def on_new_machine_alert_button_toggled(self, obj):
        self.new_machines.set_property("visible", obj.get_active())
        
    def on_close_detect_machines_clicked(self, obj):
        self.xml.get_object("new_machine_alert_button").set_active(False)
    
    def on_help_hash_id_clicked(self, obj):
        print "Todo: Fill-me"
    
    def on_cancel_registration_clicked(self, obj):
        model, iteration = self.get_selects(self.new_machines_tree)
        
        if not iteration:
            return
        
        hash_id = model.get_value(iteration, 1)
        iter = self.detect_machine_iters.pop(hash_id)
        session = self.machine_auth_pending.pop(hash_id)
        self.new_machines_detect_list_store.remove(iter)
        session.close_session()
        self.update_new_machines_state()
        
    def on_register_machine_button_clicked(self, obj):
        model, iteration = self.get_selects(self.new_machines_tree)
        
        if not iteration:
            return
        
        hash_id = model.get_value(iteration, 1)
        iter = self.detect_machine_iters.pop(hash_id)
        session = self.machine_auth_pending.pop(hash_id)
        self.new_machines_detect_list_store.remove(iter)
        
        self.xml.get_object("new_machine_alert_button").set_active(False)
        dlg = dialogs.AddMachine(Parent=self.mainwindow, Manager=self)
        data = dlg.run({'hash_id': hash_id})
        
        if data:
            self.instmachine_manager.allow_machine(hash_id, data, session)
        else:
            session.close_session()
        
        self.update_new_machines_state()
        
    def on_authorization_machine(self, hash_id, session):
        if not hash_id in self.machine_auth_pending:
            iter = self.new_machines_detect_list_store.append(
                                (session.client_address[0], hash_id))
            
            self.detect_machine_iters[hash_id] = iter
        else:
            iter = self.detect_machine_iters[hash_id]
            self.new_machines_detect_list_store.set(iter,
                                                    0,
                                                    session.client_address[0])
        
        self.machine_auth_pending[hash_id] = session
        self.update_new_machines_state()
        
    def on_delete_machine(self, obj, hash_id):
        iter = self.machines_iters.pop(hash_id)
        self.machine_list_store.remove(iter)
    
    def on_update_machine(self, obj, machine_inst):
        iter = self.machines_iters[machine_inst.hash_id]
        self.machine_list_store.set(iter,
                                treeview.MACHINE_CEL_HOST, machine_inst.name)
    
    def on_update_total_to_pay_machine(self, obj, machine_inst, total_to_pay):
        iter = self.machines_iters[machine_inst.hash_id]
        self.machine_list_store.set(iter,
                            treeview.MACHINE_CEL_PAY, "%0.2f" % total_to_pay)
    
    def on_new_machine(self, obj, inst):
        
        icon = self.get_icon_by_machine_inst(inst)
        lst = (inst.id, icon, inst.source, inst.name, "", "", "", 0,  "", 0, "")
        iter = self.machine_list_store.append(lst)
        self.machines_iters[inst.hash_id] = iter
        
        if not inst.session:
            return
        
        show_notifications = self.gconf_client.get_bool(
                       '/apps/openlh-server/ui/show_notifications')
        
        if show_notifications and self.tray.notifysuport:
            if inst.status == 0:
                title = _('%s Disconnected') % inst.name
                msg = _('%s is now Offline') % inst.name
            
            elif inst.status == 1:
                title = _('%s Connected') % inst.name
                msg = _('%s is now Available') % inst.name
            
            nt = self.tray.notify_msg(title, msg, in_status_icon=False)
            
            if nt:
                nt.show()
    
    def on_machine_status_changed(self, obj, machine_instance):
        
        assert self.machines_iters[machine_instance.hash_id]
        
        icon = self.get_icon_by_machine_inst(machine_instance)
        
        iter = self.machines_iters[machine_instance.hash_id]
        
        self.machine_list_store.set(iter,
                                    treeview.MACHINE_CEL_PIXMAP, icon,
                                    treeview.MACHINE_CEL_SOURCE,
                                    machine_instance.source)
        
        show_notifications = self.gconf_client.get_bool(
                            '/apps/openlh-server/ui/show_notifications')
        
        if show_notifications and self.tray.notifysuport:
            if machine_instance.status == 0:
                title = _('%s Unavailable')
                msg = _('%s is now Unavailable')
            elif machine_instance.status == 1:
                title = _('%s Available')
                msg = _('%s is now Available')
            elif machine_instance.status == 2:
                title = _('%s Busy')
                msg = _('%s is now Busy')
            
            nt = self.tray.notify_msg(title % machine_instance.name,
                                      msg % machine_instance.name,
                                      in_status_icon=False)
            
            if nt:
                nt.show()
        
        if machine_instance.status == 2 and machine_instance.user_id:
            full_name = self.users_manager.get_full_name(
                                        user_id=machine_instance.user_id)
            
            self.machine_list_store.set(iter,
                                        treeview.MACHINE_CEL_USER, full_name)
        else:
            self.machine_list_store.set(iter, treeview.MACHINE_CEL_USER, None)
        
        if machine_instance.status == 2:
            self.update_status_for_machine_inst(machine_instance)
        else:
            self.machine_list_store.set(iter,
                                        treeview.MACHINE_CEL_TIME_ELAPSED, "",
                                        treeview.MACHINE_CEL_TIME_ELAPSED_PROGRESS, 0,
                                        treeview.MACHINE_CEL_TIME, "",
                                        treeview.MACHINE_CEL_REMAING, "",
                                        treeview.MACHINE_CEL_PROGRESS, 0,
                                        treeview.MACHINE_CEL_PAY, "")
    ## Cash Flow Callbacks
    def on_monthly_toggle_toggled(self, obj):
        status = obj.get_active()
        self.xml.get_object('monthly_align').set_sensitive(status)
        self.date_daily_calendar.set_sensitive(not(status))
        
        if status:
            self.on_cash_flow_calendar_monthly_mode_changed(obj)
        else:
            widget = self.daily_calendar
            self.on_cash_flow_calendar_day_selected(widget)
    
    ## Other
    def on_machine_tgbnt_toggled(self, obj):
        if obj.get_active():
            self.set_page_selected(0)
    def on_users_tgbnt_toggled(self, obj):
        if obj.get_active():
            self.set_page_selected(1)
    def on_cash_flow_tgl_toggled(self, obj):
        if obj.get_active():
            self.set_page_selected(2)
    def on_open_debts_radio_btn_toggled(self, obj):
        if obj.get_active():
            self.set_page_selected(3)

    def on_window_machine_mnu_activate(self, obj):
        self.set_page_selected(0)
    def on_window_users_mnu_activate(self, obj):
        self.set_page_selected(1)
    def on_window_cash_flow_mnu_activate(self, obj):
        self.set_page_selected(2)
    def on_open_debts_mnu_activate(self, obj):
        self.set_page_selected(3)
    
    def on_show_toolbar_menu_toggled(self, obj):
        status = obj.get_active()

        self.gconf_client.set_bool("/apps/openlh-server/ui/show_toolbar",
                                   status)
        self.xml.get_object('MainToolbar').set_property("visible", status)

    def on_show_status_bar_menu_toggled(self, obj):
        status = obj.get_active()
        
        self.gconf_client.set_bool("/apps/openlh-server/ui/show_status_bar",
                                    status)
        self.statusbar.set_property("visible", status)

    def on_show_side_bar_menu_toggled(self, obj):
        status = obj.get_active()

        self.gconf_client.set_bool("/apps/openlh-server/ui/show_side_bar",
                                   status)
        self.xml.get_object('sidebar_vbox').set_property("visible", status)

    ## Cash Flow
    def get_cash_flow_type_by_int(self, cash_flow_type):
        if cash_flow_type == CASH_FLOW_TYPE_CREDIT_IN:
            type_str = _("Credit In")
        elif cash_flow_type == CASH_FLOW_TYPE_CREDIT_OUT:
            type_str = _("Credit Out")
        elif cash_flow_type == CASH_FLOW_TYPE_MACHINE_USAGE_IN:
            type_str = _("Machine Usage")
        elif cash_flow_type == CASH_FLOW_CUSTOM_TYPE_IN:
            type_str = _("Custom In")
        elif cash_flow_type == CASH_FLOW_CUSTOM_TYPE_OUT:
            type_str = _("Custom Out")
        return type_str
        
    def add_cash_flow_row(self, year, month, day, type, 
                                user, value, notes, hour):
        
        if user:
            username = user.full_name
        else:
            username = _("Unknown user")
        
        the_time = datetime.date(int(year), int(month), int(day))
        
        self.cash_flow_list_store.append((the_time.strftime('%x'),
                                          hour, 
                                          self.get_cash_flow_type_by_int(type),
                                          username,
                                          notes,
                                          "%0.2f" % value))
        
        if type in CASH_FLOW_TYPE_IN:
            self.cash_flow_total_in += value
        else:
            self.cash_flow_total_out += value
        
        self.update_status_label_for_cash_flow()
        
    def update_status_label_for_cash_flow(self):
        if self.selpage == 2:
            if self.cash_flow_status_msg_id:
                self.statusbar.remove(0, self.cash_flow_status_msg_id)
            
            message = (_("Cash in: %0.2f, Cash out: %0.2f") % 
                                                (self.cash_flow_total_in,
                                                 self.cash_flow_total_out))
            
            self.cash_flow_status_msg_id = self.statusbar.push(0, message)
        
    def clear_cash_flow(self):
        self.cash_flow_list_store.clear()

    def populate_cash_flow_by_date(self, year, month, day=None):
        self.clear_cash_flow()
        
        self.cash_flow_total_in = 0
        self.cash_flow_total_out = 0
        self.cash_flow_total = 0

        sensitive = False
        
        kwargs = {"year": year, "month": month}
            
        if day:
            kwargs["day"] = day
        
        for item in self.cash_flow_manager.get_all().filter_by(**kwargs):
            
            sensitive = True
            
            self.add_cash_flow_row(year=item.year,
                                   month=item.month,
                                   day=item.day,
                                   type=item.type,
                                   user=item.user,
                                   value=item.value,
                                   notes=item.notes,
                                   hour=item.hour)
            
        self.cash_flow_tree.set_sensitive(sensitive)
        self.cash_flow_tree.columns_autosize()

    def on_cash_flow_calendar_day_selected(self, obj):
        year, month, day = obj.get_date()
        month += 1 #Change range(0, 11) to range(1, 12)
        self.populate_cash_flow_by_date(year, month, day)

    def on_cash_flow_calendar_month_changed(self, obj):
        year, month, day = obj.get_date()
        month += 1 #Change range(0, 11) to range(1, 12)
        
        days = self.cash_flow_manager.get_days(year=year, month=month)
        obj.clear_marks()

        for day in days:
            obj.mark_day(day)
        

    def on_cash_flow_insert(self, obj, item):
        
        sdaily = self.xml.get_object("daily_radio_bnt").get_active()
        cdaily = self.xml.get_object("day_classic_toggle").get_active()
        classic = self.xml.get_object("classic_mode_radio").get_active()
        
        cyear = self.xml.get_object("year_classic").get_value_as_int()
        cmonth = self.xml.get_object("month_classic").get_active() +1
        cday = self.xml.get_object("day_classic").get_value()
        
        cal = self.daily_calendar
        syear, smonth, sday = cal.get_date()
        smonth += 1 #Change range(0, 11) to range(1, 12)
        
        if (classic and cdaily) or (not(classic) and sdaily):
            if classic:
                year, month, day = cyear, cmonth, cday
            else:
                year, month, day = syear, smonth, sday
                
            if item.month==month and item.year==year:
                cal.mark_day(item.day)
            
                if item.day==day:
                    self.cash_flow_tree.set_sensitive(True)
                    
                    self.add_cash_flow_row(year, month, day, item.type,
                                           item.user, item.value,
                                           item.notes, item.hour
                                           )
                    
                    self.update_status_label_for_cash_flow()
            
        else:
            if classic:
                year, month = cyear, cmonth
            else:
                year = int(self.xml.get_object("monthly_year").get_value())
                month = self.xml.get_object("monthly_combo").get_active() +1
            
            if item.month==month and item.year==year:
                self.cash_flow_tree.set_sensitive(True)
                
                self.add_cash_flow_row(year, month, item.day, item.type,
                                       item.user, item.value,
                                       item.notes, item.hour
                                       )
                
                self.update_status_label_for_cash_flow()

    def on_cash_flow_calendar_monthly_mode_changed(self, obj):
        year = self.xml.get_object("monthly_year").get_value_as_int()
        month = self.xml.get_object("monthly_combo").get_active() +1
        self.populate_cash_flow_by_date(year, month)
    
    def on_classic_cash_flow_changed(self, obj):
        year = self.xml.get_object("year_classic").get_value_as_int()
        month = self.xml.get_object("month_classic").get_active() +1
        
        if self.xml.get_object("day_classic_toggle").get_active():
            day = self.xml.get_object("day_classic").get_value()
        else:
            day = None
        
        self.populate_cash_flow_by_date(year, month, day)
    
    def on_day_classic_toggle_toggled(self, obj):
        self.xml.get_object("day_classic").set_sensitive(obj.get_active())
    
    def on_day_classic_output(self, obj):
        obj.set_text("%02d" % obj.get_adjustment().get_value())
        return True
    
    ##View modes
    def set_view_mode(self, side_bar_mode=True):
        if side_bar_mode:
            self.xml.get_object("sidebar_vbox").show()
            self.xml.get_object("classic_hbox").hide()
            self.xml.get_object("machines_classic_alignment").hide()
            self.xml.get_object("classic_users_alignment").hide()
            self.xml.get_object("classic_opendebts_align").hide()
            self.xml.get_object("side_bar_mode_radio").set_active(True)
            
            widget = self.xml.get_object("machines_classic_hbox")
            if self.machine_search_entry in widget.get_children():
                widget.remove(self.machine_search_entry)
            
            widget = self.xml.get_object("classic_users_hbox")
            if self.user_search_entry in widget.get_children():
                widget.remove(self.user_search_entry)
            
            widget = self.xml.get_object("classic_cash_flow_hbox")
            if self.cash_flow_search_entry in widget.get_children():
                widget.remove(self.cash_flow_search_entry)
            
            widget = self.xml.get_object("filter_open_debts_hbox")
            if self.open_debts_search_entry in widget.get_children():
                widget.remove(self.open_debts_search_entry)
            
            self.xml.get_object("find_machines_alignment").add(
                                                self.machine_search_entry)
            self.xml.get_object("find_users_alignment").add(
                                                self.user_search_entry)
            self.xml.get_object("sidebar_cash_flow_align").add(
                                                self.cash_flow_search_entry)
            self.xml.get_object("sidebar_opendebts_align").add(
                                                self.open_debts_search_entry)
        else:
            self.xml.get_object("machines_types_tree").set_cursor((0,))
            self.xml.get_object("classic_mode_radio").set_active(True)
            self.xml.get_object("sidebar_vbox").hide()
            self.xml.get_object("classic_hbox").show()
            self.xml.get_object("machines_classic_alignment").show()
            self.xml.get_object("classic_users_alignment").show()
            self.xml.get_object("classic_opendebts_align").show()
            
            widget = self.xml.get_object("find_machines_alignment")
            if self.machine_search_entry in widget.get_children():
                widget.remove(self.machine_search_entry)
            
            widget = self.xml.get_object("find_users_alignment")
            if self.user_search_entry in widget.get_children():
                widget.remove(self.user_search_entry)
            
            widget = self.xml.get_object("sidebar_cash_flow_align")
            if self.cash_flow_search_entry in widget.get_children():
                widget.remove(self.cash_flow_search_entry)
            
            widget = self.xml.get_object("sidebar_opendebts_align")
            if self.open_debts_search_entry in widget.get_children():
                widget.remove(self.open_debts_search_entry)
            
            self.xml.get_object("machines_classic_hbox").pack_start(
                                self.machine_search_entry, expand=False)
            self.xml.get_object("classic_users_hbox").pack_start(
                                self.user_search_entry, expand=False)
            self.xml.get_object("classic_cash_flow_hbox").pack_start(
                                self.cash_flow_search_entry, expand=False)
            self.xml.get_object("filter_open_debts_hbox").pack_start(
                                self.open_debts_search_entry, expand=False)
        
        self.xml.get_object("notebook").set_show_tabs(not(side_bar_mode))
        self.gconf_client.set_bool('/apps/openlh-server/ui/show_side_bar',
                                   side_bar_mode)
        
    def on_classic_mode_toggled(self, obj):
        if obj.get_active():
            self.set_view_mode(False)
    
    def on_side_bar_mode_toggled(self, obj):
        if obj.get_active():
            self.set_view_mode(True)
    
    def on_notebook_switch_page(self, obj, page, page_num):
        if self.notebook_interative:
            self.notebook_interative = False
            self.set_page_selected(page_num)
            self.notebook_interative = True

    #timeout loops
    def update_status_for_machine_inst(self, machine):

        iter = self.machines_iters[machine.hash_id]

        if machine.limited:
            assert len(machine.time) == 2
            time_str = "%0.2d:%0.2d" % machine.time
            
        else:
            time_str = _("Unlimited")
        
        time_elapsed_str = "%0.2d:%0.2d:%0.2d" % humanize_time(
                                            machine.get_elapsed_time())
        
        if machine.limited:
            time_elapsed_per = int(machine.get_time_elapsed_percentage())
            time_last_str = "%0.2d:%0.2d:%0.2d" % humanize_time(
                                            machine.get_last_time())
            time_last_per = int(machine.get_last_time_percentage())
        else:
            time_elapsed_per = 0
            time_last_str = _("None")
            time_last_per = 0

        self.machine_list_store.set(iter,
                                    treeview.MACHINE_CEL_TIME, time_str,
                                    treeview.MACHINE_CEL_TIME_ELAPSED,
                                    time_elapsed_str,
                                    treeview.MACHINE_CEL_TIME_ELAPSED_PROGRESS,
                                    time_elapsed_per,
                                    treeview.MACHINE_CEL_REMAING, time_last_str,
                                    treeview.MACHINE_CEL_PROGRESS, time_last_per)

    def on_update_machines_time(self):
        gobject.timeout_add(1000, self.on_update_machines_time)

        for machine in self.instmachine_manager.machines_by_id.values():
            
            if machine.status != 2: #busy
                continue
            
            self.update_status_for_machine_inst(machine)
    
    #Open Debts
    def set_open_debts_selected_page(self, page_num=0):
        self.notebook_interative = False
        
        self.xml.get_object(
            "open_debts_notebook").set_current_page(page_num)
        self.xml.get_object(
            "classic_open_debts_categories_combobox").set_active(page_num)
        
        if self.xml.get_object("notebook").get_current_page() == 3:
        
            if page_num == 0:
                seltreemnu = self.open_debts_machine_treemnu
            elif page_num == 1:
                seltreemnu = self.open_debts_other_treemnu
        
            self.columns_mnu.remove_submenu()
            self.columns_mnu.set_submenu(seltreemnu)
            seltreemnu.show()
        
        self.notebook_interative = True
        
    def on_open_debts_types_tree_cursor_changed(self, obj):
        model = obj.get_model()
        
        if obj.get_cursor()[0]:
            index = obj.get_cursor()[0][0]
        else:
            index = 0

        id = model[index][0]
        self.set_open_debts_selected_page(id)
    
    def on_classic_open_debts_categories_combobox_changed(self, obj):
        if not self.notebook_interative:
            return
        
        self.set_open_debts_selected_page(obj.get_active())
    
    def on_paid_open_debts_machine(self, obj):
        model, iteration = self.get_selects(self.xml.get_object(
                                            "open_debts_machine_treeview"))
        
        if not iteration:
            return
        
        id = int(model.get_value(iteration, 0))
        
        oitem = self.open_debts_machine_manager.get_all().filter_by(id=id).one()
        
        #Insert Entry in Cash Flow
        lctime = localtime()
        current_hour = "%0.2d:%0.2d:%0.2d" % lctime[3:6]
        
        citem = CashFlowItem()
        citem.type = CASH_FLOW_TYPE_MACHINE_USAGE_IN
        citem.value = oitem.value
        citem.user_id = oitem.user_id
        citem.notes = oitem.notes
        citem.year = lctime[0]
        citem.month = lctime[1]
        citem.day = lctime[2]
        citem.hour = current_hour
        
        self.cash_flow_manager.insert(citem)
        self.open_debts_machine_manager.delete(oitem)
    
    def on_paid_open_debts_other(self, obj):
        print "on_paid_open_debts_machine"
    
    def on_view_history(self, obj):
        if self.selpage == 0:
            self.on_view_history_machine(obj)
        elif self.selpage == 1:
            self.on_view_history_user(obj)
    
    def on_clear_history(self, obj):
        dlg = dialogs.clear_history(Parent=self.mainwindow)
        data = dlg.run()
        
        if not data:
            return
        
        all_entries, year, month = data
        
        if all_entries:
            self.history_manager.clear_all()
        else:
            if month == 0:
                self.history_manager.clear_by_year(year)
            else:
                self.history_manager.clear_by_year_and_month(year, month)
    
    # Plugins
    def on_plugins_clicked(self, obj):
        """
            Show "Configure Plugins" Window
        """
        dlg = PluginsWindow(MainWindow=self, Daemon=self.daemon,
                            Parent=self.mainwindow)
        dlg.run()
    
    def on_ticket_suport_cb(self, client, cnxn_id, entry, what):
        value = entry.get_value().get_bool()
        ui_manager3  = self.xml.get_object("uimanager3")
        
        widget = ui_manager3.get_widget('ticket_menuitem')
        
        if value:
            widget.show()
        else:
            widget.hide()
    
    #Machine Categories
    def get_machine_category_selected(self, obj, path):
        selection = obj.get_selection()
        
        rows = selection.get_selected_rows()
        
        if path[0] not in rows[0]:
            selection.unselect_all()
            selection.select_path(path[0])
        
        model, iteration = self.get_selects(obj)
        value = model.get_value(iteration, 0)
        
        return value
    
    def on_machines_categories_tree_activate(self, obj, path, column):
        value = self.get_machine_category_selected(obj, obj.get_cursor())
        if not value:
            return
        
        self.edit_category_clicked(None)
    
    def on_machines_categories_press_event(self, obj, event):
        if event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS:
            
            path = obj.get_path_at_pos(int(event.x), int(event.y))
            
            if not path:
                menu = self.xml.get_object("category_menu2")
                menu.popup(None, None, None, event.button, event.get_time())
                return
            
            value = self.get_machine_category_selected(obj, path)
            
            if not value:
                return
            
            id, mode = value
            if (id != 0) and (mode == None):
                widget = self.xml.get_object('category_menu')
                widget.popup(None, None, None, event.button, event.get_time())
            
    def on_machines_categories_cursor_changed(self, obj):
        
        value = self.get_machine_category_selected(obj, obj.get_cursor())
        if not value:
            return
        
        self.machine_filter_category, self.machine_filter_status = value
        
        gobject.idle_add(self.machine_filtered.refilter)
    
    def check_machine_filter(self, machine_id):
        
        #if All Machines is selected
        if ((self.machine_filter_category == 0) 
                and (self.machine_filter_status == None)):
            return True
        
        #if machine is not found in InstManager
        if not machine_id in self.instmachine_manager.machines_by_id:
            return False
        
        machine = self.instmachine_manager.machines_by_id[machine_id]
        
        #if machine.category is filter_category and not seletect a status
        if ((machine.category_id == self.machine_filter_category) 
                and (self.machine_filter_status == None)):
            return True
        
        #if all machines is seletect with a status
        if ((self.machine_filter_category == 0) 
                and (machine.status == self.machine_filter_status)):
            return True
        
        #if machine.category is filter_category and seletect with a status
        elif ((machine.category_id == self.machine_filter_category) 
                and (machine.status == self.machine_filter_status)):
            return True
        
        else:
            return False
    
    def add_new_category_clicked(self, obj):
        dlg = dialogs.MachineCategory(Parent=self.mainwindow)
        data = dlg.run()
        
        if data:
            c = MachineCategory()
            
            for key, value in data.items():
                setattr(c, key, value)
            
            try:
                self.machine_category_manager.insert(c)
            except IntegrityError:
                pass #TODO: show dialog
    
    def on_insert_category_machine(self, manager, category):
        self.populate_category_machine(category.id, category.name)
    
    def on_delete_category_machine(self, manager, category_id):
        if category_id in self.category_machines_iters:
            iter = self.category_machines_iters[category_id]
            self.machines_category_model.remove(iter)
            
            treeview = self.xml.get_object("machines_types_tree")
            treeview.set_cursor((0,))
    
    def on_update_category_machine(self, manager, category):
        if category.id in self.category_machines_iters:
            iter = self.category_machines_iters[category.id]
            self.machines_category_model.set(iter,
                                            2, "<b>%s</b>" % category.name)
    
    def delete_category_clicked(self, obj):
        treeview = self.xml.get_object("machines_types_tree")
        value = self.get_machine_category_selected(treeview, treeview.get_cursor())
        if not value:
            return
        
        id, mode = value
        
        c = self.machine_category_manager.get_all().filter_by(id=id).one()
        
        #remove associed machines
        for i in self.machine_manager.get_all().filter_by(category_id=c.id):
            if not i in self.instmachine_manager.machines_by_id:
                pass
            
            machine_inst = self.instmachine_manager.machines_by_id[i.id]
            self.instmachine_manager.update(machine_inst, {'category_id': 0})
        
        self.machine_category_manager.delete(c)
        
    def edit_category_clicked(self, obj):
        treeview = self.xml.get_object("machines_types_tree")
        value = self.get_machine_category_selected(treeview, treeview.get_cursor())
        
        if not value:
            return
        
        id, mode = value
        
        if id == 0:
            return
        
        c = self.machine_category_manager.get_all().filter_by(id=id).one()
        
        dlg = dialogs.MachineCategory(Parent=self.mainwindow)
        data = dlg.run(category=c)
        
        if data:
            for key, value in data.items():
                setattr(c, key, value)
            
            try:
                self.machine_category_manager.update(c)
            except IntegrityError:
                pass #TODO: show dialog