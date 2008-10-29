#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008 Wilson Pinto Júnior (N3RD3X) <n3rd3x@guake-terminal.org>
#  Copyright (C) 2008 Gabriel Falcão <gabriel@nacaolivre.org>
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
import re
from gtk.gdk import pixbuf_new_from_file
from os import path, listdir
from OpenlhClient.globals import *

class Icons:
    def __init__(self, icon_path=ICON_PATH):
        """
            OpenLanhouse icons library
        """
        self.icon_path = icon_path
        self.icons = self.get_icons()
        
    def construct_icon(self, icon):
        """
            Construct gtk.gdk.Pixbuf Icon
        """
        if path.exists(icon):
            return pixbuf_new_from_file(icon)
        #else:
            #print ERR_001 % icon #USE LOGGING
    
    def get_icons(self):
        """
            Get all icons in image folder
        """
        dirs = listdir(self.icon_path)
        icons = []
        REGEX = re.compile(r'(?P<name>[(\w)-]+).png')
        
        for folder in dirs:
            tmp = REGEX.match(folder)
            if tmp:
                icons.append(tmp.group('name'))
        
        return icons
        
    def get_icon(self, name):
        """
            Construct gtk.gdk.Pixbuf from name
        """
        fname = name + '.png'
        if name in self.icons:
            return self.construct_icon(path.join(self.icon_path, fname))
        #else:
            #print ERR_001 % name #USE LOGGING
    
    def get_path_icon(self, name):
        """
            Get real path for icon by name
        """
        fname = name + '.png'
        if name in self.icons:
            return os.path.join(self.icon_path, fname)
        #else:
            #print ERR_001 % name #USE LOGGING
        
