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


from os import path as ospath
from os import listdir as os_listdir
from glob import glob1

PLUGINS = []

init_path = ospath.abspath(__file__)
PLUGINS_PATH = ospath.dirname(init_path)

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
del init_path
del py_plugins_files
__all__ = tuple(PLUGINS)
