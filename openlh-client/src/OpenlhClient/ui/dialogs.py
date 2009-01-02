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
import logging
import gobject

from OpenlhClient import utils
from OpenlhClient.ui import icons
from OpenlhClient.globals import *
from OpenlhCore.utils import threaded, is_in_path, execute_command
from OpenlhClient.ui.utils import get_gtk_builder
_ = gettext.gettext

from os import name as osname
from os import path as ospath
from os import environ as osenviron

BUTTONS = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
           gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)

GNOME_OPEN_PATH = is_in_path('gnome-open')

(URL_TYPE_SITE,
 URL_TYPE_EMAIL) = range(2)

@threaded
def open_link(obj, link, url_type):
    if url_type == URL_TYPE_SITE:
        command = [GNOME_OPEN_PATH, link]
    elif url_type == URL_TYPE_EMAIL:
        command = [GNOME_OPEN_PATH, "mailto:" + link]
    
    execute_command(command)

if GNOME_OPEN_PATH:
    gtk.about_dialog_set_email_hook(open_link, URL_TYPE_EMAIL)
    gtk.about_dialog_set_url_hook(open_link, URL_TYPE_SITE)

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
        
        self.run()
        self.destroy()

class yes_no:
    def __init__(self, text, Parent=None, title=None,
                    ICON=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO,
                    default_response=gtk.RESPONSE_YES):
        """
            Dialog contains two buttons: yes and no
        """
        logger = logging.getLogger('dialogs.yes_no')
        logger.debug('Building dialog')
        dlg = gtk.MessageDialog(Parent, gtk.DIALOG_MODAL, ICON, buttons, text)
        
        if title:
            logger.debug('Setting up title')
            dlg.set_title(title)
            
        dlg.set_markup(text)
        logger.debug('Showing dialog')
        tmp = dlg.run()
        self.response = tmp == default_response
        self.get_response = lambda : self.response
        logger.debug('Destroing dialog')
        dlg.destroy()

class delete:
    def __init__(self, text, Parent=None, ICON=gtk.MESSAGE_QUESTION):
        """
            Create exit Dialog
        """
        
        self.logger = logging.getLogger('dialogs.lete')
        
        self.logger.debug('Building dialog')
        self.dlg = gtk.MessageDialog(Parent,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        ICON, gtk.BUTTONS_NONE, text)
        
        self.dlg.set_markup(text)
        self.hbox = self.dlg.vbox.get_children()[2]
        self.state = None
        
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
        
        self.logger.debug('Showing dialog')
        
        self.dlg.run()
        
    def get_sel(self):
        """
            Get name of response
        """
        return self.state
        
    def callback(self, widget, state):
        """
            Callback to get response
        """
        self.state = state
        self.dlg.destroy()
        
class ok_only:
    def __init__(self, text, Parent=None, title=None, ICON=gtk.MESSAGE_INFO):
        """
            Dialog contain only ok button
        """
        
        dlg = gtk.MessageDialog(Parent, gtk.DIALOG_MODAL, ICON,
                                                        gtk.BUTTONS_OK, text)
        
        if title:
            dlg.set_title(title)
            
        dlg.set_markup(text)
        dlg.run()
        dlg.destroy()

class calendar: #TODO: REMOVE-ME
    def __init__(self, Parent=None, title=None):
        """
            Calendar dialog
            @example:
            @app = calendar(Parent=window, title='Openlh Calendar')
            @date = app.get_date()
        """
        
        self.dlg = gtk.Dialog(title, Parent,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, BUTTONS)
        
        self.calendar = gtk.Calendar()
        self.dlg.vbox.pack_start(self.calendar)
        self.calendar.show_all()
        
        self.response = self.dlg.run()
        self.date = self.calendar.get_date()
        self.get_date = lambda : self.date
        self.dlg.destroy()

class FileChooserDialog(gtk.FileChooserDialog):
    """
        Non-blocking FileChooser Dialog around gtk.FileChooserDialog
    """
    def __init__(self, title_text, buttons, default_response, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            select_multiple=False, current_folder=None, on_response_ok=None,
            on_response_cancel = None):

        gtk.FileChooserDialog.__init__(self, title=title_text, 
            action=action, buttons=buttons)
        
        if default_response:
            self.set_default_response(default_response)
        
        self.set_select_multiple(select_multiple)
        
        if current_folder and ospath.isdir(current_folder):
            self.set_current_folder(current_folder)
        else:
            self.set_current_folder(utils.get_documents_path())
        
        self.response_ok, self.response_cancel = \
            on_response_ok, on_response_cancel
        # in gtk+-2.10 clicked signal on some of the buttons in a dialog
        # is emitted twice, so we cannot rely on 'clicked' signal
        #self.connect('response', self.on_dialog_response)
        
    def on_dialog_response(self, dialog, response):
        if response in (gtk.RESPONSE_CANCEL, gtk.RESPONSE_CLOSE):
            if self.response_cancel:
                if isinstance(self.response_cancel, tuple):
                    self.response_cancel[0](dialog, *self.response_cancel[1:])
                
                else:
                    self.response_cancel(dialog)
            
            else:
                self.just_destroy(dialog)
        
        elif response == gtk.RESPONSE_OK:
            if self.response_ok:
                if isinstance(self.response_ok, tuple):
                    self.response_ok[0](dialog, *self.response_ok[1:])
                
                else:
                    self.response_ok(dialog)
            
            else:
                self.just_destroy(dialog)
        
        
    def just_destroy(self, widget):
        self.destroy()
    
    def run(self):
        self.show_all()

class ImageChooserDialog(FileChooserDialog):
    def __init__(self, path_to_file = '', on_response_ok = None,
                                            on_response_cancel = None):
                                                
        """
            Optionally accepts path_to_snd_file so it has that as selected
        """
        def on_ok(widget, callback):
            """
                check if file exists and call callback
            """
            
            path_to_file = self.get_filename()
            if not path_to_file:
                return
            
            path_to_file = utils.decode_filechooser_file_paths(
                (path_to_file,))[0]
            
            if ospath.exists(path_to_file):
                callback(widget, path_to_file)

        try:
            if osname == 'nt':
                path = utils.get_my_pictures_path()
                
            else:
                path = osenviron['HOME']
            
        except:
            path = ''
        
        FileChooserDialog.__init__(self, title_text=_('Choose Image'),
                action = gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK),
                default_response = gtk.RESPONSE_OK,
                current_folder = path,
                on_response_ok = (on_ok, on_response_ok),
                on_response_cancel = on_response_cancel)

        filter = gtk.FileFilter()
        filter.set_name(_('All files'))
        filter.add_pattern('*')
        self.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name(_('Images'))
        filter.add_mime_type('image/png')
        filter.add_mime_type('image/jpeg')
        filter.add_mime_type('image/gif')
        filter.add_mime_type('image/tiff')
        filter.add_mime_type('image/svg+xml')
        filter.add_mime_type('image/x-xpixmap') # xpm
        self.add_filter(filter)
        self.set_filter(filter)

        if path_to_file:
            self.set_filename(path_to_file)
        
        if osname == 'posix' and ospath.exists('/usr/share/pixmaps'):
            self.add_shortcut_folder('/usr/share/pixmaps')

        self.set_use_preview_label(False)
        self.previewidget = gtk.Image()
        self.set_preview_widget(self.previewidget)
        self.connect('selection-changed', self.update_preview)

    def update_preview(self, widget):
        path_to_file = widget.get_preview_filename()
        if path_to_file is None or ospath.isdir(path_to_file):
            # nothing to preview or directory
            # make sure you clean image do show nothing
            widget.get_preview_widget().set_from_file(None)
            return
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path_to_file,
                                                PREVIEW_SIZE, PREVIEW_SIZE)
            
        except gobject.GError:
            return
        
        widget.get_preview_widget().set_from_pixbuf(pixbuf)

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
        
        if osname == 'posix' and ospath.exists('/usr/share/pixmaps'): #
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

class ConnectServer:
    def __init__(self):
        self.xml = get_gtk_builder("connect_server")
        
        self.dialog = self.xml.get_object('dialog')
        self.host = self.xml.get_object('host')
        self.connect_button = self.xml.get_object('connect_button')
        
        self.xml.connect_signals(self)
    
    def on_change_host(self, obj):
        self.connect_button.set_sensitive(bool(obj.get_text()))
    
    def run(self):
        if self.dialog.run():
            host = self.host.get_text()
            self.dialog.hide()
            return host
        
        self.dialog.hide()
