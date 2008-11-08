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

class props:
    APP_NAME = None
    CONFIG_FILE = None
    CONFIG_CLIENT = None
    DEFAULTS = {}

props = props()

#Try import gconf
try:
    import gconf
    HAS_GCONF = True
except ImportError:
    HAS_GCONF = False

#default config parser
import ConfigParser

class ConfClient:

    auto_salve = True

    def __init__(self):
        self.config_parser = ConfigParser.ConfigParser()
        self.read_file()

    def read_file(self):
        """
        Read the config file 
        """
        self.config_parser.read(props.CONFIG_FILE)

    def parse_key(self, key):
        a = key.split("/", 1)

        if not len(a) == 2:
            c = "main"
            k = key
        else:
            c = a[0]
            k = a[1]

        return c, k

    def set_string(self, key, value):
        c, k = self.parse_key(key)
        self.config_parser.set(c, k, value)
        
        if self.auto_save:
            self.write_file()

    def get_string(self, key):
        c, k = self.parse_key(key)
        
        if self.config_parser.has_option(c, k):
            return self.config_parser.get(c, k)
        elif key in props.DEFAULTS:
            return props.DEFAULTS[key]

class GconfClient:
    def __init__(self):
        pass

def config_init(appname, config_file, defaults):
    props.APPNAME = appname
    props.CONFIG_FILE = config_file
    props.DEFAULTS = defaults
    props.CONFIG_CLIENT = ConfClient()

def get_default_client():
    return props.CONFIG_CLIENT
