#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008-2009 Wilson Pinto Júnior <wilsonpjunior@gmail.com>
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

from sys import path as syspath
from os import path as ospath
from os import listdir as os_listdir
from glob import glob1
from OpenlhServer.globals import INSTALLED, PREFIX

PLUGINS = []

if INSTALLED:
    PLUGINS_PATH = ospath.join(PREFIX, "lib", 
                               "OpenlhServer",
                               "plugins")
else:
    PLUGINS_PATH = ospath.abspath(
        ospath.join("..", "plugins"))

del INSTALLED

PARENT_DIR = ospath.dirname(PLUGINS_PATH)

#Add all plugins files *.py
py_plugins_files = glob1(PLUGINS_PATH, "*.py")
for py_plugin_file in py_plugins_files:
    if py_plugin_file != "__init__.py":
        PLUGINS.append(py_plugin_file.replace(".py", ""))

#Add all dirs with contain __init__.py:
for file in os_listdir(PLUGINS_PATH):
    path = ospath.join(PLUGINS_PATH, file)
    if ospath.isdir(path) and not(file.startswith(".")) \
            and ospath.exists(ospath.join(path, "__init__.py")):
        PLUGINS.append(file)

#del used dependencies
del ospath
del glob1
#del py_plugins_files
__all__ = tuple(PLUGINS)

PLUGINS_GLOBALS = globals()
#read all plugins
syspath.insert(0, PARENT_DIR)
from plugins import *
syspath.remove(PARENT_DIR)
del PARENT_DIR

def get_plugin(plugin_name):
    if not plugin_name in PLUGINS_GLOBALS:
        return
    
    plugin = PLUGINS_GLOBALS[plugin_name]
    return plugin

def get_plugin_name(plugin):
    if hasattr(plugin, "PLUGIN_NAME"):
        return plugin.PLUGIN_NAME

def get_plugin_description(plugin):
    if hasattr(plugin, "PLUGIN_DESCRIPTION"):
        return plugin.PLUGIN_DESCRIPTION

def get_plugin_author(plugin):
    if hasattr(plugin, "PLUGIN_AUTHOR"):
        return plugin.PLUGIN_AUTHOR

def get_plugin_copyright(plugin):
    if hasattr(plugin, "PLUGIN_COPYRIGHT"):
        return plugin.PLUGIN_COPYRIGHT

def get_plugin_site(plugin):
    if hasattr(plugin, "PLUGIN_SITE"):
        return plugin.PLUGIN_SITE
