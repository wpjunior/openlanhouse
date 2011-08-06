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

from distutils.core import setup
import py2exe
import glob
import sys
import os

sys.path.append('src')
# Use local gtk folder instead of the one in PATH that is not latest gtk
if 'gtk' in os.listdir('.'):
    sys.path.append('gtk/bin')

opts = {
    'py2exe': {
        # ConfigParser,UserString,roman are needed for docutils
        'includes': 'pango,atk,gobject,cairo,pangocairo,gtk.keysyms,encodings,encodings.*,ConfigParser,UserString',
        'dll_excludes': [
            'iconv.dll','intl.dll','libatk-1.0-0.dll',
            'libgdk_pixbuf-2.0-0.dll','libgdk-win32-2.0-0.dll',
            'libglib-2.0-0.dll','libgmodule-2.0-0.dll',
            'libgobject-2.0-0.dll','libgthread-2.0-0.dll',
            'libgtk-win32-2.0-0.dll','libpango-1.0-0.dll',
            'libpangowin32-1.0-0.dll','libcairo-2.dll',
            'libpangocairo-1.0-0.dll','libpangoft2-1.0-0.dll',
            ],
        'excludes': ['docutils'],
    }
}

setup(name = 'OpenLanhouse Server',
      version = '0.2git',
      description = 'OpenSource LAN House Server',
      author = 'Wilson Pinto Júnior <wilsonpjunior@gmail.com>',
      url = 'http://openlanhouse.org/',
      license = 'GPLv3',
      windows = [{'script': 'src/openlh-server',
                  #'icon_resources': [(1, 'data/pixmaps/gajim.ico')]
                  }
                 ],
                options=opts,
                data_files=[("data/ui", glob.glob("data\ui\*.ui")),
                            ("data/icons/status", glob.glob("data\icons\status\*.png")),
                            ("data/icons", glob.glob("data\icons\*.png"))],
	
	)
	
