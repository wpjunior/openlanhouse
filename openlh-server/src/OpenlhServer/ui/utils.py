#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008-2009 Wilson Pinto Júnior <wilson@openlanhouse.org>
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
import threading
from os.path import join as os_join

from OpenlhServer.globals import *

def gthreaded(f):
    """
        Threads Wrapper
    """
    def wrapper(*args):
        gtk.gdk.threads_init()
        t = threading.Thread(target=f, args=args)
        t.setDaemon(True)
        t.start()
        gtk.gdk.threads_leave()
    wrapper.__name__ = f.__name__
    wrapper.__dict__ = f.__dict__
    wrapper.__doc__ = f.__doc__
    return wrapper

def color_entry(entry, color=None):
    """
        Modify Color into gtk.Entry
    """
    if color:
        color = gtk.gdk.color_parse(color)
    
    for state in [gtk.STATE_NORMAL, gtk.STATE_ACTIVE]:
        entry.modify_bg(state, color)
        entry.modify_base(state, color)

def get_gtk_builder(name):
    filename = os_join(UI_PATH, "%s.ui" % name)
    assert ospath.exists(filename)
    b = gtk.Builder()
    b.set_property("translation-domain", I18N_APP)
    b.add_from_file(filename)
    return b
