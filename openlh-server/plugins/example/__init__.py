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

PLUGIN_NAME = "Example"
PLUGIN_DESCRIPTION = "Plugin Example"
PLUGIN_AUTHOR = "Wilson Pinto Júnior <wilsonpjunior@gmail.com>"
PLUGIN_COPYRIGHT = "Copyright 2008 Wilson Pinto Júnior"
PLUGIN_SITE = "http://openlanhouse.org"

def enable(daemon, main_window):
    main_window.statusbar.hide()
    print "enable teste", daemon, main_window
    
def disable(daemon, main_window):
    main_window.statusbar.show()
    print "disable teste", daemon, main_window

def configure(daemon, main_window):
    print "configure", daemon, main_window
