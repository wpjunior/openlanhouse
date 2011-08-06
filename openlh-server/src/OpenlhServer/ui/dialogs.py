#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008 Wilson Pinto Júnior <wilsonpjunior@gmail.com>
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
import logging
import gobject
import datetime
import time
import webbrowser

from OpenlhServer.globals import *
_ = gettext.gettext

from os import name as osname
from os import path as ospath
from os import remove as os_remove
from os import getenv as os_getenv
from time import localtime
from threading import Lock

from OpenlhServer.ui import icons, DateEdit, HourEntry
from OpenlhServer.ui.SearchEntry import SearchEntry
from OpenlhServer.ui.utils import color_entry, get_gtk_builder

from OpenlhServer.utils import user_has_avatar, get_user_avatar_path, generate_ticket
from OpenlhServer.db.models import CashFlowItem, User

from OpenlhCore.utils import md5_cripto
from OpenlhCore.utils import calculate_time, calculate_credit
from OpenlhCore.utils import check_nick, check_name
from OpenlhCore.utils import is_in_path, execute_command, threaded
from OpenlhCore.ConfigClient import get_default_client

GNOME_OPEN_PATH = is_in_path('gnome-open')

(URL_TYPE_SITE,
 URL_TYPE_EMAIL) = range(2)

@threaded
def gnome_open_link(obj, link, url_type):
    if url_type == URL_TYPE_SITE:
        command = [GNOME_OPEN_PATH, link]
    elif url_type == URL_TYPE_EMAIL:
        command = [GNOME_OPEN_PATH, "mailto:" + link]
    
    execute_command(command)

@threaded
def common_open_link(obj, link, url_type):
    if url_type == URL_TYPE_SITE:
        webbrowser.open(link)

if GNOME_OPEN_PATH:
    open_link = gnome_open_link
    gtk.about_dialog_set_email_hook(open_link, URL_TYPE_EMAIL) #GNOME supports email
    
else:
    open_link = common_open_link

gtk.about_dialog_set_url_hook(open_link, URL_TYPE_SITE)
gtk.link_button_set_uri_hook(open_link, URL_TYPE_SITE)

class about(gtk.AboutDialog):
    def __init__(self, logo, Parent=None):
        
        gtk.AboutDialog.__init__(self)
        
        page = ()
        
        if APP_AUTHORS:
            page = page + (_("Developers:"),) + APP_AUTHORS + ('',)
        
        if APP_CONTRIB:
            page = page + (_('Contributors:'),) + APP_CONTRIB
        
        if Parent:
            self.set_transient_for(Parent)
        
        self.set_name(_("OpenLanhouse"))
        self.set_version(APP_VERSION)
        
        self.set_website(APP_SITE)
        self.set_website_label(_('OpenLanhouse Website'))
        self.set_logo(logo)
        self.set_copyright(APP_COPYRIGHT)
        self.set_comments(APP_COMMENTS)
        self.set_authors(page)
        self.set_documenters(APP_DOCS)
        self.set_artists(APP_ARTISTS)
        self.set_license(APP_LICENCE)
        
        # TRANSLATORS
        lang = os_getenv('LANG', 'en_US').split('.')[0]
        if lang in APP_TRANSLATORS:
            translator = APP_TRANSLATORS[lang]
            self.set_translator_credits(translator)
        else:
            self.set_translator_credits(_("translator-credits"))
        
        self.run()
        self.destroy()

class yes_no(gtk.MessageDialog):
    def __init__(self, text, Parent=None, title=None,
                    ICON=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO,
                    default_response=gtk.RESPONSE_YES):
        
        gtk.MessageDialog.__init__(self, Parent, gtk.DIALOG_MODAL,
                                   ICON, buttons, text)
        
        if title:
            self.set_title(title)
            
        self.set_markup(text)
        
        self.response = self.run() == default_response
        self.destroy()

class delete(gtk.MessageDialog):
    def __init__(self, text, Parent=None, ICON=gtk.MESSAGE_QUESTION):
        
        gtk.MessageDialog.__init__(self, Parent,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        ICON, gtk.BUTTONS_NONE, text)
        
        self.set_markup(text)
        childrens = self.vbox.get_children()
        if childrens == 3:
            self.hbox = childrens[2]
	else:
            self.hbox = childrens[0]

        self.response = None
        
        #Buttons
        bnt1 = gtk.Button(stock=gtk.STOCK_CANCEL, use_underline=True)
        bnt2 = gtk.Button(stock=gtk.STOCK_DELETE, use_underline=True)
        
        self.hbox.pack_start(bnt1)
        self.hbox.pack_start(bnt2)
        
        bnt1.show()
        bnt2.show()
        
        #conect
        bnt1.connect("clicked", self.callback, False)
        bnt2.connect("clicked", self.callback, True)
        
        self.run()
        
    def callback(self, widget, response):
        """
            Callback to get response
        """
        self.response = response
        self.destroy()
        
class exit(gtk.MessageDialog):
    def __init__(self, text, Parent=None, 
                 allow_miminize=True, ICON=gtk.MESSAGE_QUESTION):
        """
            Create exit Dialog
        """
        
        gtk.MessageDialog.__init__(self, Parent, gtk.DIALOG_MODAL, ICON, 
                                   gtk.BUTTONS_NONE, text)
        
        self.set_markup(text)
        childrens = self.vbox.get_children()
        if childrens == 3:
            self.hbox = childrens[2]
	else:
            self.hbox = childrens[0]

        self.response = None
        
        #Buttons
        if allow_miminize:
            bnt1 = gtk.Button(label=_('Miminize to _Tray'), use_underline=True)
        
        bnt2 = gtk.Button(stock=gtk.STOCK_NO, use_underline=True)
        bnt3 = gtk.Button(stock=gtk.STOCK_YES, use_underline=True)
        bnts = [bnt2, bnt3]
        
        if allow_miminize:
            bnts.insert(0, bnt1)
        
        for bnt in bnts:
            self.hbox.pack_start(bnt)
            bnt.show()
        
        #conect
        if allow_miminize:
            bnt1.connect("clicked", self.callback, 2) #Minimize
        
        bnt2.connect("clicked", self.callback, gtk.RESPONSE_CANCEL)
        bnt3.connect("clicked", self.callback, gtk.RESPONSE_YES)
        
        self.run()
        self.destroy()
        
    def callback(self, widget, response):
        """
            Callback to get response
        """
        self.response = response
        self.destroy()

class ok_only(gtk.MessageDialog):
    def __init__(self, text, Parent=None, title=None, ICON=gtk.MESSAGE_INFO):
        
        gtk.MessageDialog.__init__(self, Parent, gtk.DIALOG_MODAL, ICON,
                                   gtk.BUTTONS_OK, text)
        
        if title:
            self.set_title(title)
            
        self.set_markup(text)
        self.run()
        self.destroy()

class image_chooser_button(gtk.FileChooserButton):
    def __init__(self):
        gtk.FileChooserButton.__init__(self, title='Choose Image')
        
        self.toggle = gtk.CheckButton("Preview images")
        self.set_extra_widget(self.toggle)
        self.toggle.set_active(True)
        self.toggle.connect('toggled', self.toggled_cb)
        self.toggle.show()
        self.use_preview = True
        
        filter = gtk.FileFilter()
        filter.set_name(_('All files'))
        filter.add_pattern('*')
        self.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name(_('Images') )
        filter.add_mime_type('image/png')
        filter.add_mime_type('image/jpeg')
        filter.add_mime_type('image/gif')
        filter.add_mime_type('image/tiff')
        filter.add_mime_type('image/svg+xml')
        filter.add_mime_type('image/x-xpixmap')
        self.add_filter(filter)
        self.set_filter(filter)
        
        if osname == 'posix' and ospath.exists('/usr/share/pixmaps'):
            self.add_shortcut_folder('/usr/share/pixmaps')
        
        self.set_use_preview_label(False)
        self.previewidget = gtk.Image()
        self.set_preview_widget(self.previewidget)
        self.connect("update-preview", self.update_preview_cb, self.previewidget)
        
    def update_preview_cb(self, file_chooser, preview):
        
        if not self.use_preview:
            return
        
        filename = file_chooser.get_preview_filename()
        
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename,
                                            PREVIEW_SIZE, PREVIEW_SIZE)
            self.previewidget.set_from_pixbuf(pixbuf)
            self.have_preview = True
            
        except:
            self.have_preview = False
        
        self.set_preview_widget_active(self.have_preview)
        return
    
    def toggled_cb(self, obj):
        if obj.get_active():
            filename = self.get_preview_filename()
            
            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename,
                                            PREVIEW_SIZE, PREVIEW_SIZE)
                self.previewidget.set_from_pixbuf(pixbuf)
                self.have_preview = True
            except:
                self.have_preview = False
            
            self.set_preview_widget_active(self.have_preview)
            self.use_preview = True
        
        else:
            self.set_preview_widget_active(False)
            self.use_preview = False

class ImageChooserDialog(gtk.FileChooserDialog):
    def __init__(self, parent=None):
        gtk.FileChooserDialog.__init__(self, title='Choose Image',
                                       parent=parent,
                                       action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                       buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                                gtk.STOCK_OPEN, gtk.RESPONSE_OK,
                                                _("_No Image"), gtk.RESPONSE_NONE))
        
        self.toggle = gtk.CheckButton("Preview images")
        self.set_extra_widget(self.toggle)
        self.toggle.set_active(True)
        self.toggle.connect('toggled', self.toggled_cb)
        self.toggle.show()
        self.use_preview = True
        
        filter = gtk.FileFilter()
        filter.set_name(_('All files'))
        filter.add_pattern('*')
        self.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name(_('Images') )
        filter.add_mime_type('image/png')
        filter.add_mime_type('image/jpeg')
        filter.add_mime_type('image/gif')
        filter.add_mime_type('image/tiff')
        filter.add_mime_type('image/svg+xml')
        filter.add_mime_type('image/x-xpixmap')
        self.add_filter(filter)
        self.set_filter(filter)
        
        if osname == 'posix' and ospath.exists('/usr/share/pixmaps'):
            self.add_shortcut_folder('/usr/share/pixmaps')
        
        self.set_use_preview_label(False)
        self.previewidget = gtk.Image()
        self.set_preview_widget(self.previewidget)
        self.connect("update-preview", self.update_preview_cb, self.previewidget)
        
    def update_preview_cb(self, file_chooser, preview):
        
        if not self.use_preview:
            return
        
        filename = file_chooser.get_preview_filename()
        
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename,
                                            PREVIEW_SIZE, PREVIEW_SIZE)
            self.previewidget.set_from_pixbuf(pixbuf)
            self.have_preview = True
            
        except:
            self.have_preview = False
        
        self.set_preview_widget_active(self.have_preview)
        return
    
    def toggled_cb(self, obj):
        if obj.get_active():
            filename = self.get_preview_filename()
            
            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename,
                                            PREVIEW_SIZE, PREVIEW_SIZE)
                self.previewidget.set_from_pixbuf(pixbuf)
                self.have_preview = True
            except:
                self.have_preview = False
            
            self.set_preview_widget_active(self.have_preview)
            self.use_preview = True
        
        else:
            self.set_preview_widget_active(False)
            self.use_preview = False
    
    def run(self):
        response = gtk.FileChooserDialog.run(self)
        file = self.get_filename()
        self.hide()
        return response, file

class user_edit:
    
    ui_file = 'edit_user'
    nick_found = False
    
    data = {}
    data['notes'] = ""
    data['address'] = ""
    data['birth'] = None
    data['category_id'] = 0
    
    input = {}
    errs = []
    warns = []
    faults = []
    category_iters = {}
    
    user_avatar = None
    accept_first_new = False
    insert_connect_id = 0
    
    def __init__(self, manager, Parent=None):
        
        self.manager = manager
        self.users_manager = manager.users_manager
        
        self.insert_connect_id = self.manager.user_category_manager.connect(
                                            'insert', 
                                            self.on_insert_category_user)
        
        self.xml = get_gtk_builder(self.ui_file)
        self.xml.connect_signals(self)

        self.users = self.xml.get_object('users')
        self.users.set_modal(True)
        
        self.buttonbox = self.xml.get_object("buttonbox")
        self.notes = self.xml.get_object('notes')
        self.address = self.xml.get_object('address')
        self.cancel_bnt = self.xml.get_object('cancel_bnt')
        self.user_avatar_button = self.xml.get_object('user_avatar_button')
        self.user_avatar_image = self.xml.get_object('user_avatar_image')
        
        self.ok_bnt = self.xml.get_object('ok_bnt')
        self.notesbuffer = self.notes.get_buffer()
        self.addressbuffer = self.address.get_buffer()
        self.table2 = self.xml.get_object('table2')
        
        self.xml.get_object('nick_status_image').set_from_file(None)
        
        self.birth = DateEdit.DateEdit()
        self.table2.attach(self.birth, 4, 5, 2, 3,
                           xoptions=gtk.FILL, yoptions=gtk.FILL)
        self.birth.show()
        
        self.xml.get_object('nick').connect_after("changed",
                                                  self.on_nick_changed)
        self._nick_timeout_id = 0
        
        self.reg_entry('nick')
        self.reg_entry('full_name')
        self.reg_entry('email')
        self.reg_entry('identity')
        self.reg_entry('state')
        self.reg_entry('responsible')
        self.reg_entry('city')
        self.reg_entry('phone')
        
        #categories
        self.CategoryListStore = gtk.ListStore(gobject.TYPE_INT,
                                               gobject.TYPE_STRING)
        
        self.CategoryComboBox = gtk.ComboBox(model=self.CategoryListStore)
        
        cell = gtk.CellRendererText()
        self.CategoryComboBox.pack_start(cell, True)
        self.CategoryComboBox.add_attribute(cell, 'text', 1)
        self.CategoryComboBox.set_row_separator_func(self.row_separator_func)
        
        table = self.xml.get_object("misc_table")
        table.attach(child=self.CategoryComboBox,
                     left_attach=3,
                     right_attach=4,
                     top_attach=0,
                     bottom_attach=1,
                     xoptions=gtk.FILL,
                     yoptions=gtk.EXPAND|gtk.FILL)
        
        self.xml.get_object("category_label").set_mnemonic_widget(self.CategoryComboBox)
        self.CategoryComboBox.show()
        
        #Populate categories
        iter = self.CategoryListStore.append((0, _("None")))
        self.category_iters[0] = iter
        self.CategoryComboBox.set_active_iter(iter)
        
        self.CategoryListStore.append((-1, ""))
        
        if self.manager:
            for i in self.manager.user_category_manager.get_all():
                iter = self.CategoryListStore.append((i.id, i.name))
                self.category_iters[i.id] = iter
        
        if Parent:
            self.users.set_transient_for(Parent)
        
    def connect(self):
        
        self.input['nick'].connect("changed", self.check_obj, 'nick')
        self.input['full_name'].connect("changed", self.check_obj, 'full_name')
        
    def reg_entry(self, name):
        
        widget = self.xml.get_object(name)
        self.data[name] = ""
        self.input[name] = widget
        
        return widget
        
    def on_nick_changed_done(self):
        nick_widget = self.xml.get_object('nick')
        
        if not nick_widget:
            return
        
        nick = nick_widget.get_text()
        obj = self.xml.get_object('nick_status_image')
        nick_alert_hbox = self.xml.get_object('nick_alert_hbox')
        
        if (nick != "" and 
           (MIN_NICK <= len(nick) <= MAX_NICK) and
           nick != self.data['nick']):
            
            if self.users_manager.get_all().filter_by(nick=nick).count() == 1:
                self.nick_found = True
                stock = gtk.STOCK_CANCEL
                nick_alert_hbox.show()
            else:
                self.nick_found = False
                stock = gtk.STOCK_APPLY
                nick_alert_hbox.hide()
            
            obj.set_from_stock(stock, gtk.ICON_SIZE_MENU)

        else:
            self.nick_found = False
            obj.set_from_file(None)
        
        self.check_forward_button()
    
    def check_forward_button(self):
        t = not(bool([i for i in self.faults, self.errs, self.warns if i]))
        self.ok_bnt.set_sensitive(t and not(self.nick_found))
    
    def on_insert_category_user(self, manager, category):
        iter = self.CategoryListStore.append((category.id, category.name))
        self.category_iters[category.id] = iter
        
        if self.accept_first_new:
            self.CategoryComboBox.set_active_iter(iter)
    
    def on_nick_insert_text(self, obj, new_str, length, position):
        
        position = obj.get_position()
        
        if new_str.isalpha() and new_str.isupper():
            obj.stop_emission('insert-text')
            obj.insert_text(new_str.lower(), position)
            gobject.idle_add(obj.set_position, position+1)
            
        elif new_str.isdigit() or new_str.islower():
            return
        else:
            obj.stop_emission('insert-text')
    
    def on_nick_changed(self, obj):
        
        if self._nick_timeout_id > 0:
            gobject.source_remove(self._nick_timeout_id)
        
        timeout = 1000
        
        self._nick_timeout_id = gobject.timeout_add(timeout,
                                    self.on_nick_changed_done)
    
    def on_user_avatar_clicked(self, obj):
        dlg = ImageChooserDialog()
        response, image_file = dlg.run()
        
        if response == gtk.RESPONSE_NONE:
            self.user_avatar = None
            self.user_avatar_image.set_from_icon_name("stock_person", 6)
            
            #Remove Avatar File
            if user_has_avatar(self.data['id']):
                try:
                    os_remove(get_user_avatar_path(self.data['id']))
                except Exception , e:
                    print str(e)
        
        
        if response == gtk.RESPONSE_OK:
            self.user_avatar = image_file
            
            pixbuf = gtk.gdk.pixbuf_new_from_file(image_file)
            
            if not pixbuf:
                return
            
            #Calculate resize
            height = pixbuf.get_height()
            width = pixbuf.get_width()
            
            k = width / 64.0
            l = height / 94.0
            
            if k >= l:
                x = 64
                y = height / k
            else:
                x = width / l
                y = 94
            
            pixbuf = pixbuf.scale_simple(int(x), int(y), gtk.gdk.INTERP_TILES)
            self.user_avatar_image.set_from_pixbuf(pixbuf)
        
    def reset_data(self):
        
        for key in self.input.keys():
            self.data[key] = ""
            self.input[key].set_text("")
        
        self.data['notes'] = ""
        self.data['address'] = ""
        self.data['birth'] = None
        
        self.notesbuffer.set_text("")
        self.birth.set_properties('initial-time', (time.time(),))
        
    def set_data(self, user):
        
        self.reset_data()
        
        for key in self.input:
            value = user.__getattribute__(key)
            
            if value:
                self.data[key] = value
                self.input[key].set_text(self.data[key])
        
        if user.notes:
            self.data['notes'] = user.notes
            self.notesbuffer.set_text(self.data['notes'])
        
        if user.address:
            self.data['address'] = user.address
            self.addressbuffer.set_text(self.data['address'])
        
        if user.birth:
            self.data['birth'] = user.birth
            self.birth.set_time(map(int, self.data['birth'].split('-')))
        
        self.data['category_id'] = user.category_id
        
        if user.category_id:
            if user.category_id in self.category_iters:
                iter = self.category_iters[user.category_id]
                self.CategoryComboBox.set_active_iter(iter)
        
        self.data['id'] = user.id
        
        if user_has_avatar(user.id):
            self.user_avatar_image.set_from_file(get_user_avatar_path(user.id))
            
    def get_data(self):
        
        newdata = {}
        bf = self.notesbuffer
        newdata['notes'] = bf.get_text(bf.get_start_iter(), bf.get_end_iter())
        
        bf = self.addressbuffer
        newdata['address'] = bf.get_text(bf.get_start_iter(), bf.get_end_iter())
        
        newdata['birth'] = '%s-%s-%s' % self.birth.get_time()
        
        iter = self.CategoryComboBox.get_active_iter()
        newdata['category_id'] = self.CategoryListStore.get_value(iter, 0)
        
        for key in self.input.keys():
            newdata[key] = self.input[key].get_text()
        
        return newdata
    
    def get_new_data(self):
        
        new = self.get_data()
        
        def f(x):
            return x[1] != self.data[x[0]]
        
        return dict(filter(f, zip(new.keys(), new.values())))
    
    def row_separator_func(self, model, iter):
        
        if model.get_value(iter, 0) == -1:
            return True
        else:
            return False
    
    def on_new_category_clicked(self, obj):
        if self.manager:
            self.accept_first_new = True
            self.manager.add_new_user_category_clicked(None)
            self.accept_first_new = False
    
    def run(self, user=None):
        
        if user:
            self.set_data(user)
        else:
            self.ok_bnt.set_sensitive(False)
            self.faults = ['nick', 'full_name']
            
        self.connect()
        response = self.users.run()
        
        if response == 0:
            data = self.get_new_data()
            
            for key, value in data.items():
                user.__setattr__(key, value)
            
            self.users_manager.update(user)
        
        #Avatar
        try:
            avatar_pixbuf = self.user_avatar_image.get_pixbuf()
        except ValueError:
            avatar_pixbuf = None
        
        if self.user_avatar and avatar_pixbuf:
            path = get_user_avatar_path(user.id)
            
            try:
                avatar_pixbuf.save(path, "png")
            except Exception, error:
                print error
        
        #Remove Callback
        if self.insert_connect_id:
            gobject.source_remove(self.insert_connect_id)
            self.insert_connect_id = 0
        
        self.users.destroy()
    
    def check_obj(self, obj, name):
        """
            Check gtk.Entries is Valid
        """
        
        text = obj.get_text()
        
        objs = {
                'nick': check_nick,
                'full_name': check_name
               }
        
        for i in [self.faults, self.warns, self.errs]:
            if name in i:
                i.remove(name)
        
        tmp = objs[name](text)
        
        ## Check order
        ## 0 = OK
        ## 1 = Fault
        ## 2 = Warning
        ## 3 = Error
        
        if tmp == 1:
            self.faults.append(name)
        elif tmp == 3:
            self.errs.append(name)
            color_entry(obj, COLOR_RED)
        elif tmp == 2:
            self.warns.append(name)
            color_entry(obj, COLOR_YELLOW)
        else:
            color_entry(obj)
        
        t = not(bool([i for i in self.faults, self.errs, self.warns if i]))
        self.ok_bnt.set_sensitive(t and not(self.nick_found))

class adduser(user_edit):
    
    lock = False
    ui_file = 'add_user'
    
    def __init__(self, manager, price_per_hour, Parent=None):
        
        user_edit.__init__(self, manager, Parent)
        self.cash_flow_manager = manager.cash_flow_manager
        self.price_per_hour = price_per_hour
        
        self.notebook = self.xml.get_object("notebook")
        self.faults = ['nick', 'full_name']
        
        self.help_bnt = gtk.Button(stock=gtk.STOCK_HELP)
        self.buttonbox.pack_start(self.help_bnt)
        self.help_bnt.connect("clicked", self.on_help_button_clicked)
        self.buttonbox.set_child_secondary(self.help_bnt, True)
        
        self.cancel_bnt = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.buttonbox.pack_start(self.cancel_bnt)
        self.cancel_bnt.connect("clicked", self.on_cancel_button_clicked)
        self.buttonbox.set_child_secondary(self.cancel_bnt, True)
        
        self.back_button = gtk.Button(stock=gtk.STOCK_GO_BACK)
        self.buttonbox.pack_start(self.back_button)
        self.back_button.set_sensitive(False)
        self.back_button.connect("clicked", self.on_back_button_clicked)
        
        self.ok_bnt = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        self.buttonbox.pack_start(self.ok_bnt)
        self.ok_bnt.set_sensitive(False)
        self.ok_bnt.connect("clicked", self.on_ok_bnt_clicked)
        
        self.apply_bnt = gtk.Button(stock=gtk.STOCK_SAVE)
        self.buttonbox.pack_start(self.apply_bnt)
        self.apply_bnt.set_sensitive(False)
        self.apply_bnt.connect("clicked", self.on_apply_bnt_clicked)
        self.apply_bnt.set_no_show_all(True)
        
        #Credit table
        table = self.xml.get_object("credit_table")
        
        self.credit = gtk.SpinButton(climb_rate=0.01, digits=2)
        self.credit.set_increments(0.01, 1.00)
        self.credit.set_range(0, 1000)
        self.credit.connect("value-changed", self.credit_changed)
        self.xml.get_object("credit_label").set_mnemonic_widget(self.credit)
        
        table.attach(child=self.credit,
                     left_attach=1, right_attach=2,
                     top_attach=0, bottom_attach=1)
        
        self.hour_entry = HourEntry.HourEntry()
        self.hour_entry.connect('time_changed', self.time_changed)
        table.attach(child=self.hour_entry,
                     left_attach=1, right_attach=2,
                     top_attach=1, bottom_attach=2)
        self.xml.get_object("estimated_time").set_mnemonic_widget(self.hour_entry)
        
        self.buttonbox.show_all()
        table.show_all()
        
        self.xml.get_object('password_image').set_from_file(None)
        
    def on_nick_changed_done(self):
        nick = self.xml.get_object('nick').get_text()
        obj = self.xml.get_object('nick_status_image')
        nick_alert_hbox = self.xml.get_object('nick_alert_hbox')
        
        if nick != "" and MIN_NICK <= len(nick) <= MAX_NICK:
            if self.users_manager.get_all().filter_by(nick=nick).count() == 1:
                self.nick_found = True
                stock = gtk.STOCK_CANCEL
                nick_alert_hbox.show()
                self.on_back_button_clicked(None)
            else:
                self.nick_found = False
                stock = gtk.STOCK_APPLY
                nick_alert_hbox.hide()
            
            obj.set_from_stock(stock, gtk.ICON_SIZE_MENU)

        else:
            self.nick_found = False
            obj.set_from_file(None)
        
        self.check_forward_button()
        
    def on_cancel_button_clicked(self, obj):
        self.users.destroy()
    
    def on_help_button_clicked(self, obj):
        print "on_help_button_clicked"
    
    def on_back_button_clicked(self, obj):
        if self.notebook.get_current_page() == 1:
            self.notebook.set_current_page(0)
            self.back_button.set_sensitive(False)
            self.apply_bnt.hide()
            self.ok_bnt.show()
    
    def on_ok_bnt_clicked(self, obj):
        if self.notebook.get_current_page() == 0:
            self.notebook.set_current_page(1)
            self.back_button.set_sensitive(True)
            self.apply_bnt.show()
            self.ok_bnt.hide()
    
    def on_apply_bnt_clicked(self, obj):
        data = self.get_new_data()
        password = self.xml.get_object("password_entry_1").get_text()
        
        user = User(nick=data['nick'],
                    full_name=data['full_name'],
                    password=md5_cripto(password))
        
        data.pop('nick')
        data.pop('full_name')
        
        for key, value in data.items():
            user.__setattr__(key, value)
        
        user.reg_date = datetime.datetime.now()
        
        #Credit!
        value = self.credit.get_value()
        
        if value:
            user.credit = value
        
        self.users_manager.insert(user)
        
        #Avatar
        try:
            avatar_pixbuf = self.user_avatar_image.get_pixbuf()
        except ValueError:
            avatar_pixbuf = None
        
        if self.user_avatar and avatar_pixbuf:
            path = get_user_avatar_path(user.id)
            
            try:
                avatar_pixbuf.save(path, "png")
            except Exception, error:
                print error
        
        if value:
            #Insert Entry in Cash Flow
            lctime = localtime()
            current_hour = "%0.2d:%0.2d:%0.2d" % lctime[3:6]
        
            citem = CashFlowItem()
            citem.type = CASH_FLOW_TYPE_CREDIT_IN
            citem.value = value
            citem.user_id = user.id
            citem.year = lctime[0]
            citem.month = lctime[1]
            citem.day = lctime[2]
            citem.hour = current_hour
        
            self.cash_flow_manager.insert(citem)
        
        #Remove Callback
        if self.insert_connect_id:
            gobject.source_remove(self.insert_connect_id)
            self.insert_connect_id = 0
        
        self.users.destroy()
        
    def on_show_password_toggle_toggled(self, obj):
        status = obj.get_active()
        self.xml.get_object("password_entry_1").set_visibility(status)
        self.xml.get_object("password_entry_2").set_visibility(status)
    
    def on_password_entry_changed(self, obj):
        p1 = self.xml.get_object("password_entry_1").get_text()
        p2 = self.xml.get_object("password_entry_2").get_text()
        
        if p1 == p2 and p1 != "":
            stock = gtk.STOCK_APPLY
        elif p1 == p2 and p1 == "":
            stock = None
        else:
            stock = gtk.STOCK_CANCEL
        
        self.apply_bnt.set_sensitive(p1==p2 and p1!="")
        
        if stock != None:
            self.xml.get_object("password_image").set_from_stock(stock,
                                                          gtk.ICON_SIZE_MENU)
        else:
            self.xml.get_object("password_image").set_from_file(None)
    
    def run(self):
        """
            Show dialog and return alterations
        """
        
        self.users.show()
        self.connect()
    
    def credit_changed(self, obj):
        if not self.lock:
            self.lock = True
            tm = calculate_time(self.price_per_hour, obj.get_value())
            self.hour_entry.set_time(*tm)
            self.lock = False
    
    def time_changed(self, obj):
        if not self.lock:
            self.lock = True
            t = obj.get_time()
            self.credit.set_value(calculate_credit(self.price_per_hour, *t))
            self.lock = False

class change_password:
    def __init__(self, Parent=None):
        self.dialog = gtk.Dialog(_("Change password"), Parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        
        self.dialog.set_border_width(6)
        self.dialog.set_has_separator(False)
        self.dialog.set_resizable(False)
        box = self.dialog.get_children()[0]
        box.set_spacing(12)
        
        self.cancel_bnt = self.dialog.add_button(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_REJECT)
        
        self.change_bnt = self.dialog.add_button(_("C_hange password"),
                                                 gtk.RESPONSE_ACCEPT)
        
        self.change_bnt.set_sensitive(False)
        
        self.hbox = gtk.HBox()
        self.hbox.set_spacing(12)
        self.hbox.set_border_width(6)
        box.pack_start(self.hbox)
        
        icon = gtk.image_new_from_icon_name("gtk-dialog-authentication",
                                            gtk.ICON_SIZE_DIALOG)
        icon.set_alignment(0.50, 0)
        icon.set_padding(6, 0)
        self.hbox.pack_start(icon, expand=False)
        
        self.vbox = gtk.VBox()
        self.vbox.set_spacing(6)
        self.hbox.pack_start(self.vbox)
        
        title = gtk.Label()
        
        title.set_markup(_("<b><big>Change password</big></b>\n\n"
                           "To Change the password, enter the new " 
                           "password, retype it for verification and "
                           "click <b>Change password</b>."))
        
        title.set_line_wrap(True)
        title.set_alignment(0, 0.50)
        self.vbox.pack_start(title, expand=False)
        
        self.table = gtk.Table()
        self.table.set_col_spacings(12)
        self.table.set_row_spacings(6)
        self.vbox.pack_start(self.table, expand=False, padding=6)
        
        self.password_1 = gtk.Entry()
        self.password_2 = gtk.Entry()
        
        self.password_1.set_visibility(False)
        self.password_2.set_visibility(False)
        
        self.password_1.connect("changed", self._pass_changed)
        self.password_2.connect("changed", self._pass_changed)
        
        self.table.attach(child=self.password_1,
                          left_attach=1, right_attach=2,
                          top_attach=1, bottom_attach=2)
        
        self.table.attach(child=self.password_2,
                          left_attach=1, right_attach=2,
                          top_attach=2, bottom_attach=3)
        
        label = gtk.Label(_("_New password:"))
        label.set_use_underline(True)
        label.set_alignment(0, 0.50)
        label.set_mnemonic_widget(self.password_1)
        self.table.attach(child=label,
                          left_attach=0, right_attach=1,
                          top_attach=1, bottom_attach=2,
                          xoptions=gtk.FILL, yoptions=gtk.FILL)
        
        label = gtk.Label(_("_Retype new password:"))
        label.set_use_underline(True)
        label.set_alignment(0, 0.50)
        label.set_mnemonic_widget(self.password_2)
        self.table.attach(child=label,
                          left_attach=0, right_attach=1,
                          top_attach=2, bottom_attach=3,
                          xoptions=gtk.FILL, yoptions=gtk.FILL)
        
        self.show_password = gtk.CheckButton(_("_Show password"))
        self.show_password.set_mode(False)
        self.show_password.connect("toggled", self._on_show_password_clicked)
        
        self.table.attach(child=self.show_password,
                          left_attach=1, right_attach=2,
                          top_attach=3, bottom_attach=4,
                          xoptions=gtk.FILL, yoptions=gtk.FILL)
        
    def _on_show_password_clicked(self, obj):
        status = obj.get_active()
        self.password_1.set_visibility(status)
        self.password_2.set_visibility(status)
    
    def _pass_changed(self, obj):
        pass_1 = self.password_1.get_text()
        pass_2 = self.password_2.get_text()
        
        self.change_bnt.set_sensitive(pass_1 == pass_2 and pass_1 != "")
        
    def run(self):
        self.hbox.show_all()
        r = self.dialog.run()
        password = self.password_1.get_text()
        self.dialog.destroy()
        
        if r != gtk.RESPONSE_REJECT:
            return password

class AddCredit:
    
    lock = False
    
    def __init__(self, price_per_hour, Parent=None):
        
        self.price_per_hour = price_per_hour
        
        self.xml = get_gtk_builder('add_credit')
        self.dialog = self.xml.get_object('add_credit')
        self.table = self.xml.get_object('table')
        self.credit = self.xml.get_object('credit')
        self.add_button = self.xml.get_object('add_button')
        self.textview_bf = self.xml.get_object('textview').get_buffer()

        self.hour_entry = HourEntry.HourEntry()
        self.hour_entry.show()
        self.hour_entry.connect('time_changed', self.time_changed)
        self.table.attach(child=self.hour_entry,
                          left_attach=1, right_attach=2,
                          top_attach=1, bottom_attach=2)
        
        self.xml.connect_signals(self)
    
    def show(self, all=True):
        if all:
            self.dialog.show_all()
        else:
            self.dialog.show()
    
    def run(self):
        resp = self.dialog.run()
        r = None
        notes = self.textview_bf.get_text(self.textview_bf.get_start_iter(),
                                          self.textview_bf.get_end_iter())
        
        if resp:
            r = self.credit.get_value()
            
        self.dialog.destroy()
        return r, notes
    
    def credit_changed(self, obj):
        if not self.lock:
            self.lock = True
            value = obj.get_value()
            self.add_button.set_sensitive(bool(value))
            tm = calculate_time(self.price_per_hour, value)
            self.hour_entry.set_time(*tm)
            self.lock = False
    
    def time_changed(self, obj):
        if not self.lock:
            self.lock = True
            t = obj.get_time()
            value = calculate_credit(self.price_per_hour, *t)
            self.add_button.set_sensitive(bool(value))
            self.credit.set_value(value)
            self.lock = False

class RemoveCredit:
    
    lock = False
    
    def __init__(self, users_manager, currency,
                 user_id, current_credit, Parent=None):
        
        self.users_manager = users_manager
        self.handler_id = self.users_manager.connect(
                        'credit_update', self.on_credit_update)
        
        self.currency = currency
        self.current_credit = current_credit
        self.user_id = user_id
        
        self.xml = get_gtk_builder('remove_credit')
        self.dialog = self.xml.get_object('remove_credit')
        self.current_credit_widget = self.xml.get_object('current_credit')
        self.credit = self.xml.get_object('credit')
        self.remove_button = self.xml.get_object('remove_button')
        self.textview_bf = self.xml.get_object('textview').get_buffer()
        
        self.credit.set_range(0, current_credit)
        
        self.current_credit_widget.set_label("%s %0.2f" % (currency,
                                                        self.current_credit))
        
        self.xml.connect_signals(self)
    
    def on_credit_update(self, obj, user_id, value):
        if self.user_id == user_id:
            self.current_credit = value
            self.credit.set_range(0, value)
            self.current_credit_widget.set_label("%s %0.2f" % (self.currency,
                                                        self.current_credit))
    
    def show(self, all=True):
        if all:
            self.dialog.show_all()
        else:
            self.dialog.show()
    
    def run(self):
        resp = self.dialog.run()
        r = None
        notes = self.textview_bf.get_text(self.textview_bf.get_start_iter(),
                                          self.textview_bf.get_end_iter())
        
        if resp:
            r = self.credit.get_value()
        
        self.users_manager.disconnect(self.handler_id)
        self.dialog.destroy()
        return r, notes
    
    def credit_changed(self, obj):
        self.remove_button.set_sensitive(bool(obj.get_value()))

class user_info:
    
    user_id = 0
    currency = ""
    
    def __init__(self, users_manager, Parent=None):
        
        xml = get_gtk_builder('userinfo')
        
        self.userinfo = xml.get_object('userinfo')
        self.registred = xml.get_object('registred')
        self.last_login = xml.get_object('last_login')
        self.login_count = xml.get_object('login_count')
        self.responsible = xml.get_object('responsible')
        self.user_avatar = xml.get_object('user_avatar')
        self.credit = xml.get_object('credit')
        self.email = xml.get_object('email')
        self.nick = xml.get_object('nick')
        self.full_name = xml.get_object('full_name')
        
        xml.connect_signals(self)
        
        self.xml = xml
        self.users_manager = users_manager
        
        self.handler_id = self.users_manager.connect(
                        'credit_update', self.on_credit_update)
        
        if Parent:
            self.userinfo.set_transient_for(Parent)
    
    def on_credit_update(self, obj, user_id, value):
        if self.user_id == user_id:
            self.xml.get_object('credit').set_text(
                    "%s %0.2f" % (self.currency, value)
                    )
    
    def run(self, currency, user, credit, last_machine=None):
        
        self.user_id = user.id
        self.currency = currency
        
        string_vars = ('full_name', 'nick',
                       'responsible', 'login_count', 'city', 'state',
                       'identity', 'phone')

        for name in string_vars:
            value = user.__getattribute__(name)
            
            if value != None:
                widget = self.xml.get_object(name)
                widget.set_text(str(value))
        
        self.userinfo.set_title(_('%s Properties') % user.full_name)
        
        if user.email:
            widget = self.xml.get_object('email')
            widget.set_uri("mailto:%s" % user.email)
            widget.set_label(user.email)
        else:
            self.xml.get_object('email').hide()
        
        if user.last_login:
            self.last_login.set_text(user.last_login.ctime())
        
        if last_machine:
            self.xml.get_object("last_machine").set_text(last_machine)
        
        if user.reg_date:
            self.registred.set_text(user.reg_date.ctime())
        
        if user.address:
            bf = self.xml.get_object('address').get_buffer()
            bf.set_text(user.address)

        if user.notes:
            bf = self.xml.get_object('notes').get_buffer()
            bf.set_text(user.notes)

        if user.birth:
            birth = map(int, user.birth.split('-'))
            self.xml.get_object("birth").set_text(
                    datetime.date(*birth).strftime("%x")
                    )
        
        if user.credit != None:
            self.xml.get_object('credit').set_text(
                    "%s %0.2f" % (currency, user.credit)
                    )
        
        if credit:
            self.xml.get_object('credit').set_text(
                    "%s %0.2f" % (currency, credit)
                    )
        
        if user.active:
            self.xml.get_object('active').set_text(_("True"))
        else:
            self.xml.get_object('active').set_text(_("False"))
        
        #Avatar
        if user_has_avatar(user.id):
            self.user_avatar.set_from_file(get_user_avatar_path(user.id))
        else:
            self.user_avatar.hide()
        
        self.userinfo.run()
        self.users_manager.disconnect(self.handler_id)
        self.userinfo.destroy()

class AlertAddMachine:
    response = None
    
    def __init__(self, Parent=None):
        
        self.xml = get_gtk_builder('add_machine')
        self.dialog = self.xml.get_object('alert_add_machine')
        self.dialog.set_title("")
        
        if Parent:
            self.dialog.set_transient_for(Parent)
    
    def run(self):
        r = False
        
        if self.dialog.run():
            r = True
        
        self.dialog.destroy()
        return r

class AddMachine:
    
    response = None
    faults = ['name', 'hash_id']
    accept_first_new = False
    insert_connect_id = 0
    category_iters = {}
    
    def __init__(self, Parent=None, Manager=None):
        
        self.manager = Manager
        
        self.insert_connect_id = self.manager.machine_category_manager.connect(
                                            'insert', 
                                            self.on_insert_category_machine)
        
        self.xml = get_gtk_builder('add_machine')
        
        self.dialog = self.xml.get_object('add_machine')
        self.hash_id = self.xml.get_object('hash_id')
        self.okbnt = self.xml.get_object('okbnt')
        self.description = self.xml.get_object('description')
        self.description_buffer = self.description.get_buffer()
        self.name_entry = self.xml.get_object('name_entry')
        self.cancelbnt = self.xml.get_object('cancelbnt')
        
        self.CategoryListStore = gtk.ListStore(gobject.TYPE_INT,
                                               gobject.TYPE_STRING)
        
        self.CategoryComboBox = gtk.ComboBox(model=self.CategoryListStore)
        
        cell = gtk.CellRendererText()
        self.CategoryComboBox.pack_start(cell, True)
        self.CategoryComboBox.add_attribute(cell, 'text', 1)
        self.CategoryComboBox.set_row_separator_func(self.row_separator_func)
        
        table = self.xml.get_object("table")
        table.attach(child=self.CategoryComboBox,
                     left_attach=1,
                     right_attach=2,
                     top_attach=2,
                     bottom_attach=3,
                     xoptions=gtk.FILL,
                     yoptions=gtk.EXPAND|gtk.FILL)
        
        self.xml.get_object("category_label").set_mnemonic_widget(self.CategoryComboBox)
        self.CategoryComboBox.show()
        
        #Populate categories
        iter = self.CategoryListStore.append((0, _("None")))
        self.category_iters[0] = iter
        self.CategoryComboBox.set_active_iter(iter)
        
        self.CategoryListStore.append((-1, ""))
        
        if self.manager:
            for i in self.manager.machine_category_manager.get_all():
                iter = self.CategoryListStore.append((i.id, i.name))
                self.category_iters[i.id] = iter
        
        self.xml.connect_signals(self)
        
        self.name_entry.connect('changed', self.name_entry_changed)
        self.hash_id.connect('changed', self.hash_id_changed)
        
        if Parent:
            self.dialog.set_transient_for(Parent)
    
    def hash_id_changed(self, obj):
        if len(obj.get_text()) == 40:
            if 'hash_id' in self.faults:
                self.faults.remove('hash_id')
        else:
            if not 'hash_id' in self.faults:
                self.faults.append('hash_id')
        
        self.okbnt.set_sensitive(not(bool(self.faults)))
    
    def name_entry_changed(self, obj):
        if bool(obj.get_text()):
            if 'name' in self.faults:
                self.faults.remove('name')
        else:
            if not 'name' in self.faults:
                self.faults.append('name')
        
        self.okbnt.set_sensitive(not(bool(self.faults)))
    
    def on_new_category_clicked(self, obj):
        if self.manager:
            self.accept_first_new = True
            self.manager.add_new_machine_category_clicked(None)
            self.accept_first_new = False
    
    def row_separator_func(self, model, iter):
        
        if model.get_value(iter, 0) == -1:
            return True
        else:
            return False
    
    def on_insert_category_machine(self, manager, category):
        iter = self.CategoryListStore.append((category.id, category.name))
        self.category_iters[category.id] = iter
        
        if self.accept_first_new:
            self.CategoryComboBox.set_active_iter(iter)

    def run(self, data=None, set_hash_sensitive=False):
        if data:
            if 'name' in data:
                if 'name' in self.faults:
                    self.faults.remove('name')
                
                self.name_entry.set_text(data['name'])
            
            if 'description' in data:
                self.description_buffer.set_text(data['description'])
            
            if 'category_id' in data:
                if data['category_id'] in self.category_iters:
                    iter = self.category_iters[data['category_id']]
                    self.CategoryComboBox.set_active_iter(iter)
            
            if 'hash_id' in data:
                if 'hash_id' in self.faults:
                    self.faults.remove('hash_id')
                
                self.hash_id.set_text(data['hash_id'])
        
        self.hash_id.set_sensitive(set_hash_sensitive)
        
        if self.dialog.run():
            bf = self.description_buffer
            iter = self.CategoryComboBox.get_active_iter()
            
            response = {'name': self.name_entry.get_text(),
                        'description': bf.get_text(bf.get_start_iter(),
                              bf.get_end_iter()),
                        'hash_id': self.hash_id.get_text()
                        }
            
            if iter:
                response['category_id'] = self.CategoryListStore.get_value(iter, 0)
            
            if self.insert_connect_id:
                gobject.source_remove(self.insert_connect_id)
            
            self.dialog.destroy()
            return response
        
        if self.insert_connect_id:
            gobject.source_remove(self.insert_connect_id)
        
        self.dialog.destroy()
    
    def on_help_hash_id_clicked(self, obj):
        open_link(None, HELP_HASHID_URL,
                  URL_TYPE_SITE)

class block_machine:
    def __init__(self, machine_name, Parent=None):
        self.xml = get_gtk_builder('block_machine')
        self.dialog = self.xml.get_object("dialog")
        
        if Parent:
            self.dialog.set_transient_for(Parent)
        
        self.xml.get_object("action_combo").set_active(0)
        self.xml.get_object("title").set_markup(
               _("<b><big>Are you sure you want to block \"%s\" Machine?"
                 "</big></b>\n\n"
                 "This machine is in use and if you block it, "
                 "unsaved work will be lost.") % machine_name)
        
        self.xml.connect_signals(self)
    
    def on_after_toggled(self, obj):
        self.xml.get_object("action_combo").set_sensitive(obj.get_active())
    
    def run(self):
        block = bool(self.dialog.run())
        after = self.xml.get_object("after").get_active()
        action = self.xml.get_object("action_combo").get_active()
        self.dialog.destroy()
        return block, after, action
        
class unblock_machine:
    
    hours = 0
    minutes = 0
    lock = False
    user_found = False
    user_credit = 0
    user_id = None
    pre_paid = False

    def __init__(self, currency, price_per_hour, users_manager, Parent=None):

        self.xml = get_gtk_builder('unblock_machine')
        self.dialog = self.xml.get_object("dialog")
        self.price_per_hour = price_per_hour
        self.users_manager = users_manager
        self.currency = currency

        self._user_entry_timeout_id = 0

        if Parent:
            self.dialog.set_transient_for(Parent)

        self.unregistred_radio = self.xml.get_object('unregistred_radio') 
        self.registred_radio = self.xml.get_object('registred_radio')
        self.total_to_pay = self.xml.get_object("total_to_pay")
        self.warning_label = self.xml.get_object("warning_label")
        self.user_entry = self.xml.get_object("user_entry")
        self.unlimited_radio = self.xml.get_object("unlimited_radio")
        self.limited_radio = self.xml.get_object("limited_radio")
        self.xml.get_object("user_status").set_from_file(None)
        self.xml.get_object("hourly_rate").set_value(price_per_hour)
        
        #EntryCompletion
        self.entry_completion = gtk.EntryCompletion()
        self.entry_list_store = gtk.ListStore(gobject.TYPE_STRING,
                                              gobject.TYPE_STRING)
        
        
               
        render_name = gtk.CellRendererText()
        self.entry_completion.pack_start(render_name, expand=True)
        self.entry_completion.add_attribute(render_name, "text", 0)
        
        render_nick = gtk.CellRendererText()
        self.entry_completion.pack_start(render_nick, expand=False)
        self.entry_completion.add_attribute(render_nick, "text", 1)
         
        self.entry_completion.set_property('text_column', 1)

        self.entry_completion.set_model(self.entry_list_store)
        self.entry_completion.set_match_func(self.entry_completion_match_func)
        self.user_entry.set_completion(self.entry_completion)
        self.populate_list_store()
        self.user_entry.connect("changed", self.on_user_entry_changed)

        self.xml.connect_signals(self)

    def populate_list_store(self):
        for user in self.users_manager.get_full_name_and_nick():
            self.entry_list_store.append(user)

    def entry_completion_match_func(self, completion, key, iter):
        
        model = completion.get_model()
        full_name = model.get_value(iter, 0)
        nick = model.get_value(iter, 1)
        
        if nick.startswith(key) or full_name.lower().startswith(key):
            return True
        
        return False

    def on_unregistred_radio_toggled(self, obj):
        if obj.get_active():
            self.limited_radio.set_active(True)
            self.unlimited_radio.set_sensitive(False)
            self.xml.get_object("registred_table").set_sensitive(False)
            self.xml.get_object("prepaid").set_sensitive(True)
        else:
            self.unlimited_radio.set_sensitive(True)
            self.xml.get_object("registred_table").set_sensitive(True)
            self.xml.get_object("prepaid").set_sensitive(False)
        
        self.check_credit()

    def on_limited_radio_toggled(self, obj):
        self.xml.get_object("time_alignment").set_sensitive(obj.get_active())
        self.check_credit()
    
    def on_hourly_rate_value_changed(self, obj):
        self.price_per_hour = obj.get_value()
        self.on_total_to_pay_value_changed(self.total_to_pay)

    def on_spin_button_output(self, obj):
        obj.set_text("%02d" % obj.get_adjustment().get_value())
        return True

    def on_hour_value_changed(self, obj):
        self.hours = obj.get_value_as_int()
        self.update_total_to_pay()

    def on_minutes_value_changed(self, obj):
        self.minutes = obj.get_value_as_int()
        self.update_total_to_pay()

    def update_total_to_pay(self):
        if not self.lock:
            self.lock = True
            t = calculate_credit(self.price_per_hour,
                                 self.hours,
                                 self.minutes, 0)

            self.total_to_pay.set_value(t)
            self.lock = False

    def check_credit(self):
        
        t = self.total_to_pay.get_value()

        if (self.registred_radio.get_active() and 
            ((self.limited_radio.get_active() and self.user_found
            and t > self.user_credit) or 
            (self.unlimited_radio.get_active() and self.user_found
            and self.user_credit == 0))):

            self.xml.get_object('warning_hbox').show()
            color_entry(self.total_to_pay, COLOR_YELLOW)
            self.warning_label.set_text(
                    _("The user does not have sufficient credits"))

            credit_ok = False
            
        else:
            self.xml.get_object('warning_hbox').hide()
            color_entry(self.total_to_pay, None)
            self.warning_label.set_text("")

            credit_ok = True
        
        total_to_pay = self.total_to_pay.get_value()

        if ((self.registred_radio.get_active() and self.user_found
                and credit_ok) and
            ((self.limited_radio.get_active() and total_to_pay)
                or self.unlimited_radio.get_active()) or
            (self.unregistred_radio.get_active() and total_to_pay)):
            status = True
        else:
            status = False

        self.xml.get_object('apply_button').set_sensitive(status)

    def on_total_to_pay_value_changed(self, obj):
        
        self.check_credit()

        if not self.lock:
            self.lock = True
            t = obj.get_value()

            hour, minutes, secs = calculate_time(self.price_per_hour, t)
            self.xml.get_object('hour').set_value(hour)
            self.xml.get_object('minutes').set_value(minutes)
            
            self.lock = False

    def on_user_entry_changed(self, obj):
        
        if self._user_entry_timeout_id > 0:
            gobject.source_remove(self._user_entry_timeout_id)
        
        timeout = 1000
        
        self._user_entry_timeout_id = gobject.timeout_add(timeout,
                                    self.on_user_entry_changed_done)

    def on_user_entry_changed_done(self):
        nick = self.user_entry.get_text()
        out = self.users_manager.get_credit_and_id(nick)

        if out:
            self.user_credit = out[0]
            self.user_id = out[1]
            self.xml.get_object('credit').set_text(
                    _("%s %0.2f of credit") % (self.currency,
                                               self.user_credit)
                    )

            self.user_found = True

        elif nick == "":
            self.user_found = False
            self.xml.get_object('credit').set_text("")

        else:
            self.user_found = False
            self.xml.get_object('credit').set_text(_("User not found"))
        
        self.check_credit()

    def run(self):
        
        resp = self.dialog.run()
        
        if resp:
            total_time = (
                    self.xml.get_object('hour').get_value_as_int(),
                    self.xml.get_object('minutes').get_value_as_int())
            
            
            data = {
                    'registred': self.registred_radio.get_active(),
                    'limited': self.limited_radio.get_active(),
                    'pre_paid': self.xml.get_object('prepaid').get_active(),
                    'price_per_hour': self.xml.get_object('hourly_rate').get_value()
                   }
            
            if data['registred']:
                data['user_id'] = self.user_id
            else:
                data['user_id'] = None
            
            if data['limited']:
                data['time'] = total_time
            else:
                data['time'] = None

            self.dialog.destroy()

            return data

        self.dialog.destroy()

class NewCashFlowItem:
    
    user_id = None
    user_found = True
    
    def __init__(self, users_manager, Parent=None):
        self.users_manager = users_manager
        self._user_entry_timeout_id = 0
        
        self.xml = get_gtk_builder('cash_flow_new_item')
        self.dialog = self.xml.get_object("dialog")
        self.user_nick = self.xml.get_object("user_nick")
        self.xml.get_object("type_combobox").set_active(0)
        
        #EntryCompletion
        self.entry_completion = gtk.EntryCompletion()
        self.entry_list_store = gtk.ListStore(gobject.TYPE_STRING,
                                              gobject.TYPE_STRING)
               
        render_name = gtk.CellRendererText()
        self.entry_completion.pack_start(render_name, expand=True)
        self.entry_completion.add_attribute(render_name, "text", 0)
        
        render_nick = gtk.CellRendererText()
        self.entry_completion.pack_start(render_nick, expand=False)
        self.entry_completion.add_attribute(render_nick, "text", 1)
         
        self.entry_completion.set_property('text_column', 1)

        self.entry_completion.set_model(self.entry_list_store)
        self.entry_completion.set_match_func(self.entry_completion_match_func)
        self.user_nick.set_completion(self.entry_completion)
        self.user_nick.connect("changed", self.on_user_entry_changed)
        self.populate_list_store()
        
        if Parent:
            self.dialog.set_transient_for(Parent)
        
        self.xml.connect_signals(self)
    
    def populate_list_store(self):
        for user in self.users_manager.get_full_name_and_nick():
            self.entry_list_store.append(user)

    def entry_completion_match_func(self, completion, key, iter):
        
        model = completion.get_model()
        full_name = model.get_value(iter, 0)
        nick = model.get_value(iter, 1)
        
        if nick.startswith(key) or full_name.lower().startswith(key):
            return True
        
        return False
    
    def on_user_entry_changed(self, obj):
        
        if self._user_entry_timeout_id > 0:
            gobject.source_remove(self._user_entry_timeout_id)
        
        timeout = 1000
        
        self._user_entry_timeout_id = gobject.timeout_add(timeout,
                                    self.on_user_entry_changed_done)

    def on_user_entry_changed_done(self):
        nick = self.user_nick.get_text()
        out = self.users_manager.get_credit_and_id(nick)

        if out:
            self.user_id = out[1]
            self.user_found = True
            self.xml.get_object("label_warning").hide()
            self.xml.get_object("warning_image").hide()

        elif nick == "":
            self.user_found = False
            self.xml.get_object("label_warning").hide()
            self.xml.get_object("warning_image").hide()

        else:
            self.user_found = False
            self.xml.get_object("label_warning").show()
            self.xml.get_object("warning_image").show()
        
        self.check_status()
            
    def on_checkbutton_toggled(self, obj):
        self.xml.get_object("user_nick").set_sensitive(obj.get_active())
        self.check_status()
    
    def on_value_spinbutton_value_changed(self, obj):
        self.check_status()
    
    def check_status(self):
        user_status = self.xml.get_object("checkbutton").get_active()
        value = self.xml.get_object("value_spinbutton").get_value()
        
        if ((value and not(user_status)) or 
            (value and user_status and self.user_found)):
            status = True
        else:
            status = False
        
        self.xml.get_object("ok_button").set_sensitive(status)
    
    def run(self):
        if self.dialog.run():
            data = {
                'type': self.xml.get_object("type_combobox").get_active(),
                'value': self.xml.get_object("value_spinbutton").get_value(),
                }
            
            bf = self.xml.get_object("notes_textview").get_buffer()
            data['notes'] = bf.get_text(bf.get_start_iter(), bf.get_end_iter())
            
            if self.xml.get_object("checkbutton").get_active():
                data['user_id'] = self.user_id
            
            self.dialog.destroy()
            return data
        
        self.dialog.destroy()

class machine_info:
    def __init__(self, Parent=None):
        
        xml = get_gtk_builder('machine_info')
        
        self.dialog = xml.get_object('dialog')
        self.name = xml.get_object('name')
        self.hash_id = xml.get_object('hash_id')
        self.source = xml.get_object('source')
        self.last_user = xml.get_object('last_user')
        self.textview = xml.get_object('textview')
        self.os = xml.get_object('os')
        
        xml.connect_signals(self)
        
        self.xml = xml
        
        if Parent:
            self.dialog.set_transient_for(Parent)
    
    def on_os_changed(self, machine_inst, os_name, os_version):
        self.os.set_text("%s %s" % (os_name, os_version))
        
    def on_source_changed(self, machine_inst, source):
        if source:
            self.source.set_text(source)
        else:
            self.source.set_text("")
               
    def run(self, machine_inst, last_user=None):
        self.dialog.set_title(_('%s Properties') % machine_inst.name)
        self.name.set_text(machine_inst.name)
        self.hash_id.set_text(machine_inst.hash_id)
        self.os.set_text("%s %s" % (machine_inst.os_name,
                                    machine_inst.os_version))
        
        os_changed_id = machine_inst.connect("os_changed",
                                          self.on_os_changed)
        
        source_changed_id = machine_inst.connect("source_changed",
                                                 self.on_source_changed)
        
        if machine_inst.source:
            self.source.set_text(machine_inst.source)
        
        bf = self.textview.get_buffer()
        bf.set_text(machine_inst.description)
        
        if last_user:
            self.xml.get_object("last_user").set_text(last_user)
            
        self.dialog.run()
        gobject.source_remove(os_changed_id)
        gobject.source_remove(source_changed_id)
        self.dialog.destroy()

class add_time:
    
    lock = False
    
    def __init__(self, price_per_hour, Parent=None):
        
        self.price_per_hour = price_per_hour
        
        self.xml = get_gtk_builder('add_time')
        self.dialog = self.xml.get_object('add_time')
        self.table = self.xml.get_object('table')
        self.add_button = self.xml.get_object('add_button')
        self.price = self.xml.get_object('price')
        
        self.hour_entry = HourEntry.HourEntry()
        self.hour_entry.set_second_visible(False)
        self.hour_entry.show()
        self.hour_entry.connect('time_changed', self.time_changed)
        self.table.attach(child=self.hour_entry,
                          left_attach=1, right_attach=2,
                          top_attach=0, bottom_attach=1)
        
        self.xml.connect_signals(self)
        
        if Parent:
            self.dialog.set_transient_for(Parent)
    
    def price_changed(self, obj):
        if not self.lock:
            self.lock = True
            value = obj.get_value()
            self.add_button.set_sensitive(bool(value))
            tm = calculate_time(self.price_per_hour, value)
            self.hour_entry.set_time(*tm)
            self.lock = False
    
    def time_changed(self, obj):
        if not self.lock:
            self.lock = True
            t = obj.get_time()
            value = calculate_credit(self.price_per_hour, *t)
            self.add_button.set_sensitive(bool(value))
            self.price.set_value(value)
            self.lock = False
    
    def run(self):
        a_time = None
        
        if self.dialog.run():
            a_time = self.hour_entry.get_time()
        
        self.dialog.destroy()
        return a_time

class remove_time:
    
    lock = False
    
    def __init__(self, price_per_hour, Parent=None):
        
        self.price_per_hour = price_per_hour
        
        self.xml = get_gtk_builder('remove_time')
        self.dialog = self.xml.get_object('remove_time')
        self.table = self.xml.get_object('table')
        self.remove_button = self.xml.get_object('remove_button')
        self.price = self.xml.get_object('price')
        
        self.hour_entry = HourEntry.HourEntry()
        self.hour_entry.set_second_visible(False)
        self.hour_entry.show()
        self.hour_entry.connect('time_changed', self.time_changed)
        self.table.attach(child=self.hour_entry,
                          left_attach=1, right_attach=2,
                          top_attach=0, bottom_attach=1)
        
        self.xml.connect_signals(self)
        
        if Parent:
            self.dialog.set_transient_for(Parent)
    
    def price_changed(self, obj):
        if not self.lock:
            self.lock = True
            value = obj.get_value()
            self.remove_button.set_sensitive(bool(value))
            tm = calculate_time(self.price_per_hour, value)
            self.hour_entry.set_time(*tm)
            self.lock = False
    
    def time_changed(self, obj):
        if not self.lock:
            self.lock = True
            t = obj.get_time()
            value = calculate_credit(self.price_per_hour, *t)
            self.remove_button.set_sensitive(bool(value))
            self.price.set_value(value)
            self.lock = False
    
    def run(self):
        a_time = None
        
        if self.dialog.run():
            a_time = self.hour_entry.get_time()
        
        self.dialog.destroy()
        return a_time

class history:
    search_text = ""
    
    def __init__(self, history_manager, Parent=None):
        self.history_manager = history_manager
        self.xml = get_gtk_builder('history')
        
        self.dialog = self.xml.get_object('history')
        self.dialog.set_default_size(600, 300)
        self.treeview = self.xml.get_object("treeview")
        self.calendar = self.xml.get_object("calendar")
        self.search_entry = SearchEntry(gtk.icon_theme_get_default())
        self.search_entry.show()
        
        self.search_entry.connect("terms-changed",
                                  self.on_search_entry_terms_changed)
        
        self.xml.get_object("filter_hbox").pack_start(self.search_entry)
        
        #TreeView
        model = gtk.ListStore(gobject.TYPE_INT,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              )
        
        #ID
        column = gtk.TreeViewColumn(_("ID"), gtk.CellRendererText(), text=0)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_reorderable(True)
        column.set_clickable(True)
        column.set_sort_column_id(0)
        column.set_resizable(False)
        column.set_expand(False)
        column.set_visible(False)
        
        self.treeview.append_column(column)
        
        #Time
        column = gtk.TreeViewColumn(_("Time"), gtk.CellRendererText(), text=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_reorderable(True)
        column.set_clickable(True)
        column.set_sort_column_id(1)
        column.set_resizable(True)
        column.set_expand(False)
        
        self.treeview.append_column(column)
        
        #Start Time
        column = gtk.TreeViewColumn(_("Start Time"), gtk.CellRendererText(), text=2)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_reorderable(True)
        column.set_clickable(True)
        column.set_sort_column_id(2)
        column.set_resizable(True)
        column.set_expand(False)
        
        self.treeview.append_column(column)
        
        #End Time
        column = gtk.TreeViewColumn(_("End Time"), gtk.CellRendererText(), text=3)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_reorderable(True)
        column.set_clickable(True)
        column.set_sort_column_id(3)
        column.set_resizable(True)
        column.set_expand(False)
        
        self.treeview.append_column(column)
        
        #User
        column = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=4)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_reorderable(True)
        column.set_clickable(True)
        column.set_sort_column_id(4)
        column.set_resizable(True)
        column.set_expand(False)
        
        self.treeview.append_column(column)
        self.name_column = column
        
        self.model = model
        self.model_filtered = self.model.filter_new()
        self.model_filtered.set_visible_func(self.on_model_visible_cb)
        self.model_sortable = gtk.TreeModelSort(self.model_filtered)
        self.treeview.set_model(self.model_sortable)
        self.xml.connect_signals(self)
        
        if Parent:
            self.dialog.set_transient_for(Parent)
    
    def on_search_entry_terms_changed(self, obj, text):
        self.search_text = text
        self.model_filtered.refilter()
    
    def on_model_visible_cb(self, model, iter):
        if self.search_text == "":
            return True
        
        t = False
        for col in (4,):
            x = model.get_value(iter, col)
            if x and self.search_text in x:
                t = True
                break
        
        return t
    
    def on_history_insert(self, obj, item):
        year, month, day = self.calendar.get_date()
        month += 1 #Change range(0, 11) to range(1, 12)
        
        if item.month==month and item.year==year:
            self.calendar.mark_day(item.day)
            
            if item.day==day:
                self.treeview.set_sensitive(True)
                self.append_item(item)
    
class machine_history(history):
    def __init__(self, history_manager, Parent=None):
        history.__init__(self, history_manager, Parent)
        self.name_column.set_title(_("User"))
    
    def append_item(self, item):
        if item.user:
            username = item.user.full_name
        else:
            username = _("Unknown user")
            
        self.model.append((item.id, item.time,
                           item.start_time, 
                           item.end_time, username))
    
    def populate(self, year, month, day, machine_id):
        
        self.model.clear()
        
        kwargs = {'year': year, 'month': month, 'day': day,
                  'machine_id': machine_id}
        
        sensitive = False
        
        for item in self.history_manager.get_all().filter_by(**kwargs):
            sensitive = True
            self.append_item(item)
            
        self.treeview.set_sensitive(sensitive)
    
    def on_day_selected(self, obj):
        year, month, day = self.calendar.get_date()
        month += 1 #Change range(0, 11) to range(1, 12)
        
        self.populate(year, month, day, self.machine_inst.id)
    
    def on_month_changed(self, obj):
        year, month, day = self.calendar.get_date()
        month += 1 #Change range(0, 11) to range(1, 12)
        
        days = self.history_manager.get_days_for_machine_id(year, 
                                                month, self.machine_inst.id)
        
        obj.clear_marks()

        for day in days:
            obj.mark_day(day)
    
    def run(self, machine_inst):
        self.history_manager.connect('insert',
                                     self.on_history_insert)
        self.machine_inst = machine_inst
        self.dialog.set_title(_("History of %s") % machine_inst.name)
        
        self.on_month_changed(self.calendar)
        self.on_day_selected(self.calendar)
        
        self.dialog.run()
        self.dialog.destroy()
        self.history_manager.disconnect_by_func(self.on_history_insert)

class user_history(history):
    def __init__(self, history_manager, Parent=None):
        history.__init__(self, history_manager, Parent)
        self.name_column.set_title(_("Machine"))
    
    def append_item(self, item):
        if item.machine:
            machinename = item.machine.name
        else:
            machinename = _("Unknown user")
            
        self.model.append((item.id, item.time,
                           item.start_time, 
                           item.end_time, machinename))
    
    def populate(self, year, month, day, user_id):
        
        self.model.clear()
        
        kwargs = {'year': year, 'month': month, 'day': day,
                  'user_id': user_id}
        
        sensitive = False
        
        for item in self.history_manager.get_all().filter_by(**kwargs):
            sensitive = True
            self.append_item(item)
            
        self.treeview.set_sensitive(sensitive)
    
    def on_day_selected(self, obj):
        year, month, day = self.calendar.get_date()
        month += 1 #Change range(0, 11) to range(1, 12)
        
        self.populate(year, month, day, self.user_id)
    
    def on_month_changed(self, obj):
        year, month, day = self.calendar.get_date()
        month += 1 #Change range(0, 11) to range(1, 12)
        
        days = self.history_manager.get_days_for_machine_id(year, 
                                                month, self.user_id)
        
        obj.clear_marks()

        for day in days:
            obj.mark_day(day)
    
    def run(self, user_id, user_name):
        self.history_manager.connect('insert',
                                     self.on_history_insert)
        self.user_id = user_id
        self.dialog.set_title(_("History of %s") % user_name)
        
        self.on_month_changed(self.calendar)
        self.on_day_selected(self.calendar)
        
        self.dialog.run()
        self.dialog.destroy()
        self.history_manager.disconnect_by_func(self.on_history_insert)

class clear_history:
    def __init__(self, Parent):
        self.xml = get_gtk_builder('clear_history')
        self.dialog = self.xml.get_object('clear_history')
        self.month = self.xml.get_object('month')
        self.year = self.xml.get_object('year')
        
        year, month = localtime()[0:2]
        
        self.year.set_value(year)
        self.month.set_active(month)
        
        self.xml.connect_signals(self)
        
        if Parent:
            self.dialog.set_transient_for(Parent)
    
    def on_all_entries_toggled(self, obj):
        self.xml.get_object("alignment").set_sensitive(not obj.get_active())
    
    def run(self):
        data = None
        
        if self.dialog.run():
            all_entries = self.xml.get_object("allentries").get_active()
            year = int(self.year.get_value())
            month = self.month.get_active()
            data = all_entries, year, month
        
        self.dialog.destroy()
        
        return data
        
class set_price_per_hour:
    def __init__(self, Parent=None):
        self.xml = get_gtk_builder('set_price_per_hour')
        self.dialog = self.xml.get_object('dialog')
        self.apply_button = self.xml.get_object('button2')
        self.price_per_hour = self.xml.get_object('price_per_hour')
        self.xml.connect_signals(self)
        
        if Parent:
            self.dialog.set_transient_for(Parent)
    
    def on_price_changed(self, obj):
        self.apply_button.set_sensitive(bool(
                obj.get_value()))

    def run(self):
        price = None
        if self.dialog.run():
            price = self.price_per_hour.get_value()
        
        self.dialog.destroy()
        return price

class NewTicket:

    hours = 0
    minutes = 0
    lock = False

    def __init__(self, ticket_size, hourly_rate, OpenTicketManager, Parent=None):
        self.xml = get_gtk_builder('new_ticket')
        
        self.dialog = self.xml.get_object('dialog')
        self.total_to_pay = self.xml.get_object('total_to_pay')
        
        self.open_ticket_manager = OpenTicketManager
        self.hourly_rate = hourly_rate
        self.ticket_size = ticket_size
        
        self.xml.get_object("hourly_rate").set_value(hourly_rate)

        self.xml.connect_signals(self)
        
        self.on_refresh_button_clicked(None) # write first code
        
        if Parent:
            self.dialog.set_transient_for(Parent)
            
    def on_refresh_button_clicked(self, obj):
        while True:
            code = generate_ticket(self.ticket_size)
            if not self.open_ticket_manager.ticket_exists(code):
                break

        widget = self.xml.get_object("code_entry")
        widget.set_text(code)
        
    def on_spin_button_output(self, obj):
        obj.set_text("%02d" % obj.get_adjustment().get_value())
        return True

    def on_hour_value_changed(self, obj):
        self.hours = obj.get_value_as_int()
        self.update_total_to_pay()

    def on_minutes_value_changed(self, obj):
        self.minutes = obj.get_value_as_int()
        self.update_total_to_pay()

    def update_total_to_pay(self):
        if not self.lock:
            self.lock = True
            t = calculate_credit(self.hourly_rate,
                                 self.hours,
                                 self.minutes, 0)
            
            self.xml.get_object('ok_button').set_sensitive(bool(t))
            self.total_to_pay.set_value(t)
            self.lock = False
            
            
    def on_total_to_pay_value_changed(self, obj):
        
        if not self.lock:
            self.lock = True
            t = obj.get_value()

            hour, minutes, secs = calculate_time(self.hourly_rate, t)
            self.xml.get_object('hour').set_value(hour)
            self.xml.get_object('minutes').set_value(minutes)
            
            self.xml.get_object('ok_button').set_sensitive(bool(t))

            self.lock = False
            
    def on_hourly_rate_value_changed(self, obj):
        self.hourly_rate = obj.get_value()
        self.on_total_to_pay_value_changed(self.total_to_pay)
        
    def run(self):
        if self.dialog.run():
            data = {}
            data['code'] = self.xml.get_object('code_entry').get_text()
            data['price'] = self.total_to_pay.get_value()
            data['hourly_rate'] = self.xml.get_object('hourly_rate').get_value()
            
            bf = self.xml.get_object("notes").get_buffer()
            data['notes'] = bf.get_text(bf.get_start_iter(), bf.get_end_iter())
            
            self.dialog.destroy()
            
            return data
        
        self.dialog.destroy()

class MachineCategory:
    def __init__(self, Parent=None):
        self.xml = get_gtk_builder('add_machine_category')
        
        self.dialog = self.xml.get_object('add_machine_category')
        
        self.background_chooser = image_chooser_button()
        self.logo_chooser = image_chooser_button()
        
        self.background_chooser.set_sensitive(False)
        self.logo_chooser.set_sensitive(False)
        
        background_chooser_btn = self.background_chooser.get_children()[0]
        logo_chooser_btn = self.logo_chooser.get_children()[0]
        
        #pack start
        self.xml.get_object('lock_box').attach(self.background_chooser, 1, 2, 0, 1,
                    xoptions=gtk.FILL|gtk.EXPAND, xpadding=0, ypadding=0)
        
        self.xml.get_object('lock_box').attach(self.logo_chooser, 1, 2, 1, 2,
                    xoptions=gtk.FILL|gtk.EXPAND, xpadding=0, ypadding=0)
        
        self.background_chooser.show()
        self.logo_chooser.show()
        
        self.xml.connect_signals(self)
        
        if Parent:
            self.dialog.set_transient_for(Parent)
    
    def on_name_entry_changed(self, obj):
        self.xml.get_object('okbnt').set_sensitive(bool(obj.get_text()))
    
    def background_bnt_toggled_cb(self, obj):
        self.background_chooser.set_sensitive(obj.get_active())
    
    def on_logo_bnt_toggled(self, obj):
        self.logo_chooser.set_sensitive(obj.get_active())
    
    def on_hourly_rate_toggled(self, obj):
        self.xml.get_object('price_hour').set_sensitive(obj.get_active())
        
    def set_category(self, category):
        if category.name:
            self.xml.get_object('name_entry').set_text(category.name)
        
        if category.custom_logo:
            self.xml.get_object('logo_bnt').set_active(True)
        
        if category.custom_background:
            self.xml.get_object('background_bnt').set_active(True)
        
        if category.custom_price_hour:
            self.xml.get_object('custom_hourly_rate').set_active(True)
        
        if category.price_hour:
            self.xml.get_object('price_hour').set_value(category.price_hour)
        
        if category.logo_path:
            self.logo_chooser.set_filename(category.logo_path)
        
        if category.background_path:
            self.background_chooser.set_filename(category.background_path)

    
    def run(self, category=None):
        
        if category:
            self.set_category(category)
            self.dialog.set_title("Machine Category Editor")
        
        if self.dialog.run():
            data = {}
            data['name'] = self.xml.get_object('name_entry').get_text()
            data['custom_logo'] = self.xml.get_object('logo_bnt').get_active()
            data['custom_background'] = self.xml.get_object('background_bnt').get_active()
            data['custom_price_hour'] = self.xml.get_object("custom_hourly_rate").get_active()
            
            if ('custom_price_hour' in data) and data['custom_price_hour']:
                data['price_hour'] = self.xml.get_object('price_hour').get_value()
            
            if ('custom_logo' in data) and data['custom_logo']:
                data['logo_path'] = self.logo_chooser.get_filename()
            
            if ('custom_background' in data) and data['custom_background']:
                data['background_path'] = self.background_chooser.get_filename()
        
            self.dialog.destroy()
            
            return data
        else:
            self.dialog.destroy()


class UserCategory:
    def __init__(self, Parent=None):
        self.xml = get_gtk_builder('add_user_category')
        
        self.dialog = self.xml.get_object('add_user_category')
        self.xml.connect_signals(self)
        
        if Parent:
            self.dialog.set_transient_for(Parent)
    
    def on_name_entry_changed(self, obj):
        self.xml.get_object('okbnt').set_sensitive(bool(obj.get_text()))
    
    def on_hourly_rate_toggled(self, obj):
        self.xml.get_object('price_hour').set_sensitive(obj.get_active())
    
    def set_category(self, category):
        if category.name:
            self.xml.get_object('name_entry').set_text(category.name)
        
        if category.custom_price_hour:
            self.xml.get_object('custom_hourly_rate').set_active(True)
        
        if category.price_hour:
            self.xml.get_object('price_hour').set_value(category.price_hour)
        
        if category.allow_login:
            self.xml.get_object('allow_login').set_active(True)
    
    def run(self, category=None):
        
        if category:
            self.set_category(category)
            self.dialog.set_title("User Category Editor")
        
        if self.dialog.run():
            data = {}
            data['name'] = self.xml.get_object('name_entry').get_text()
            data['price_hour'] = self.xml.get_object('price_hour').get_value()
            
            data['custom_price_hour'] = self.xml.get_object("custom_hourly_rate").get_active()
            
            if ('custom_price_hour' in data) and data['custom_price_hour']:
                data['price_hour'] = self.xml.get_object('price_hour').get_value()
            
            data['allow_login'] = self.xml.get_object("allow_login").get_active()
        
            self.dialog.destroy()
            
            return data
        else:
            self.dialog.destroy()

class SelectMachineCategory:
    
    category = 0
    
    def __init__(self, machine_category_manager, Parent=None):
        
        self.machine_category_manager = machine_category_manager
        
        self.xml = get_gtk_builder('select_machine_category')
        self.dialog = self.xml.get_object("dialog")
        
        if Parent:
            self.dialog.set_transient_for(Parent)
        
        combobox = self.xml.get_object("combobox")
        combobox.set_active(0)
        combobox.set_row_separator_func(self.row_separator_func)
        
        model = combobox.get_model()
        model.append((-1, ""))

        if self.machine_category_manager:
            for i in self.machine_category_manager.get_all():
                model.append((i.id, i.name))
                
        self.xml.connect_signals(self)

    def row_separator_func(self, model, iter):
        
        if model.get_value(iter, 0) == -1:
            return True
        else:
            return False
    
    def run(self):
        if self.dialog.run():
            combobox = self.xml.get_object("combobox")
            model = combobox.get_model()
            iter = combobox.get_active_iter()
            self.category = model.get_value(iter, 0)
            self.dialog.destroy()

            return True
        
        self.dialog.destroy()

class ViewAllTickets:
    iters = {}
    insert_id = 0
    delete_id = 0

    def __init__(self, TicketManager, Parent=None,
                 add_callback=None, remove_callback=None):
        
        self.ticket_manager = TicketManager
        self.add_callback = add_callback
        self.remove_callback = remove_callback
        
        self.xml = get_gtk_builder('view_all_tickets')
        self.dialog = self.xml.get_object("dialog")
        self.treeview = self.xml.get_object("treeview")
        
        # code, price, hourly_rate, notes
        self.ListStore = gtk.ListStore(gobject.TYPE_INT,
                                       gobject.TYPE_STRING,
                                       gobject.TYPE_STRING,
                                       gobject.TYPE_STRING,
                                       gobject.TYPE_STRING)
        self.treeview.set_model(self.ListStore)
        
        # Code
        column =  gtk.TreeViewColumn(_("Code"),
                                     gtk.CellRendererText(),
                                     text=1)
        
        column.set_sort_column_id(1)
        self.treeview.append_column(column)
        
        # Price
        column =  gtk.TreeViewColumn(_("Price"),
                                     gtk.CellRendererText(),
                                     text=2)
        
        column.set_sort_column_id(2)
        self.treeview.append_column(column)
        
        # Hourly rate
        column =  gtk.TreeViewColumn(_("Hourly rate"),
                                     gtk.CellRendererText(),
                                     text=3)
        
        column.set_sort_column_id(3)
        self.treeview.append_column(column)

        # Notes
        column =  gtk.TreeViewColumn(_("Notes"),
                                     gtk.CellRendererText(),
                                     text=4)
        
        column.set_sort_column_id(4)
        self.treeview.append_column(column)
        
        self.insert_id = self.ticket_manager.connect("insert",
                                                     self.on_ticket_insert)
        
        self.delete_id = self.ticket_manager.connect("delete",
                                                     self.on_ticket_delete)
                        
        if self.ticket_manager:
            for i in self.ticket_manager.get_all():
                iter = self.ListStore.append((i.id, i.code, 
                                              "%0.2f" % i.price,
                                              "%0.2f" % i.hourly_rate,
                                              i.notes))
                self.iters[i.id] = iter
        
        if Parent:
            self.dialog.set_transient_for(Parent)
            
        self.xml.connect_signals(self)
    
    def on_ticket_insert (self, manager, i):
        iter = self.ListStore.append((i.id, i.code, 
                                      "%0.2f" % i.price,
                                      "%0.2f" % i.hourly_rate,
                                      i.notes))
        self.iters[i.id] = iter
    
    def on_ticket_delete (self, manager, id):
        iter = self.iters.pop(id)
        self.ListStore.remove(iter)
        
    def on_remove_ticket_clicked(self, obj):
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        
        if not iter:
            return
        
        id = model.get_value(iter, 0)
        t = self.ticket_manager.get_all().filter_by(id=id).one()

        if self.remove_callback:
            self.remove_callback(t)
        
    def on_add_ticket_clicked(self, obj):
        if self.add_callback:
            self.add_callback(obj)
    
    def run(self):
        self.dialog.run()

        if self.insert_id:
            gobject.source_remove(self.insert_id)
            
        if self.delete_id:
            gobject.source_remove(self.delete_id)
            
        self.dialog.destroy()

class EditCloseApplications:
    def __init__(self, Parent=None):
        self.conf_client = get_default_client()
        self.xml = get_gtk_builder('edit_close_apps')
        self.dialog = self.xml.get_object("dialog")
        
        self.treeview = self.xml.get_object("treeview")
        
        self.ListStore = gtk.ListStore(gobject.TYPE_STRING)
        self.treeview.set_model(self.ListStore)
        
        self.renderer = gtk.CellRendererText()
        self.renderer.set_property("editable", True)
        self.renderer.connect("edited", self.column_edited)
        self.column = gtk.TreeViewColumn(_("Applications"),
                                         self.renderer,
                                         text=0)
        
        self.treeview.append_column(self.column)
        
        if Parent:
            self.dialog.set_transient_for(Parent)
            
        self.xml.connect_signals(self)
        
        #Populate apps
        for a in self.conf_client.get_string_list("close_apps_list"):
            self.ListStore.append((a,))

    def column_edited(self, renderer, path_string, text):
        
        iter = self.ListStore.get_iter_from_string(path_string)
        old_text = self.ListStore.get_value(iter, 0)
        
        # not accept spaces
        if text == _("Application name"):
            self.ListStore.remove(iter)
            return

        if " " in text:
            text = text.split(" ")[0]

        if not(text):
            if old_text == _("Application name"):
                self.ListStore.remove(iter)
            return
        
        # remove iter
        
        
        self.ListStore.set_value(iter, 0, text)
    
    def on_add_button_clicked(self, obj):
        iter = self.ListStore.append((_("Application name"),))
        path = self.ListStore.get_path(iter)
        self.treeview.set_cursor_on_cell(path, self.column,
                                         self.renderer,
                                         start_editing=True)
                
    def on_remove_button_clicked(self, obj):
        cursor = self.treeview.get_cursor()
        iter = self.ListStore.get_iter(cursor[0])
        self.ListStore.remove(iter)
        self.treeview.grab_focus()
    
    def run(self):
        self.dialog.run()

        # save apps
        apps = []
        for i in self.ListStore:
            app_name = i[0]

            if app_name == _("Application name"):
                continue
            
            if " " in app_name:
                app_name = app_name.split(" ")[0]
                
            apps.append(app_name)
            
        self.conf_client.set_string_list("close_apps_list",
                                         apps)

        self.dialog.destroy()
        
class NewDebt:
    def __init__(self, users_manager, Parent=None):
        self.xml = get_gtk_builder('add_opendebt')
        self.dialog = self.xml.get_object("dialog")
        
        self.users_manager = users_manager

        self._user_entry_timeout_id = 0

        if Parent:
            self.dialog.set_transient_for(Parent)

        self.total_to_pay = self.xml.get_object("total_to_pay")
        self.warning_label = self.xml.get_object("warning_label")
        self.user_entry = self.xml.get_object("user_entry")
        self.xml.get_object("user_status").set_from_file(None)
        
        #EntryCompletion
        self.entry_completion = gtk.EntryCompletion()
        self.entry_list_store = gtk.ListStore(gobject.TYPE_STRING,
                                              gobject.TYPE_STRING)
        
        
        render_name = gtk.CellRendererText()
        self.entry_completion.pack_start(render_name, expand=True)
        self.entry_completion.add_attribute(render_name, "text", 0)
        
        render_nick = gtk.CellRendererText()
        self.entry_completion.pack_start(render_nick, expand=False)
        self.entry_completion.add_attribute(render_nick, "text", 1)
         
        self.entry_completion.set_property('text_column', 1)

        self.entry_completion.set_model(self.entry_list_store)
        self.entry_completion.set_match_func(self.entry_completion_match_func)
        self.user_entry.set_completion(self.entry_completion)
        self.populate_list_store()
        
        self.xml.connect_signals(self)
        
    def run(self):
        s = self.dialog.run()

        if not s:
            self.dialog.destroy()
            return
            
        data = {}
        data['user'] = self.xml.get_object('user_entry').get_text()
        data['value'] = self.xml.get_object('debt_value').get_value()
        
        bf = self.xml.get_object('notes').get_buffer()
        data['notes'] = bf.get_text(bf.get_start_iter(),
                                    bf.get_end_iter())

        self.dialog.destroy()
        return data

    def entry_completion_match_func(self, completion, key, iter):
        
        model = completion.get_model()
        full_name = model.get_value(iter, 0)
        nick = model.get_value(iter, 1)
        
        if nick.startswith(key) or full_name.lower().startswith(key):
            return True
        
        return False

    def populate_list_store(self):
        for user in self.users_manager.get_full_name_and_nick():
            self.entry_list_store.append(user)

    def on_user_entry_changed(self, obj):
        
        if self._user_entry_timeout_id > 0:
            gobject.source_remove(self._user_entry_timeout_id)
        
        timeout = 1000
        
        self._user_entry_timeout_id = gobject.timeout_add(timeout,
                                    self.on_user_entry_changed_done)

    def on_user_entry_changed_done(self):
        nick = self.user_entry.get_text()
        out = self.users_manager.get_credit_and_id(nick)

        if out:
            self.user_found = True
            self.xml.get_object('found_status').set_text("")

        elif nick == "":
            self.user_found = False
            self.xml.get_object('found_status').set_text("")

        else:
            self.user_found = False
            self.xml.get_object('found_status').set_text(_("User not found"))
        
        self.xml.get_object('ok_button').set_sensitive(self.user_found)
        
        if self.user_found:
            self.xml.get_object('user_status').set_from_stock('gtk-apply',
                                                              gtk.ICON_SIZE_MENU)
        else:
            self.xml.get_object('user_status').set_from_file(None)
