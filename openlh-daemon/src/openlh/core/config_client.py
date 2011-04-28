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

from os import path as ospath
import ConfigParser

try:
    from gi.repository import GConf
    HAS_GCONF = True
except ImportError:
    HAS_GCONF = False

APP_NAME = None
CONFIG_FILE = None
CONFIG_CLIENT = None
DEFAULTS = {}

class ConfClient:

    auto_save = True

    def __init__(self):
        self.config_parser = ConfigParser.ConfigParser()
        self.read_file()

    def read_file(self):
        """
        Read the config file 
        """
        self.config_parser.read(CONFIG_FILE)

    def write_file(self):
        """
        Write the config file
        """
        file = open(CONFIG_FILE, "wb")
        self.config_parser.write(file)

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
        
        if not self.config_parser.has_section(c):
            self.config_parser.add_section(c)
        
        # remove option because the value is equal with default value
        if (key in DEFAULTS) and (DEFAULTS[key] == value):
           self.config_parser.remove_option(c, k)
        else:
            self.config_parser.set(c, k, str(value))
        
        if self.auto_save:
            self.write_file()

    set_float = set_string
    set_bool = set_string
    set_int = set_string
    
    def set_string_list(self, key, value):
        c, k = self.parse_key(key)
        
        if not self.config_parser.has_section(c):
            self.config_parser.add_section(c)
        
        # remove option because the value is equal with default value
        if (key in DEFAULTS) and (list(DEFAULTS[key]) == list(value)):
            self.config_parser.remove_option(c, k)
        else:
            self.config_parser.set(c, k, ", ".join(value))
        
        if self.auto_save:
            self.write_file()
    
    # Getters
    def get_string(self, key):
        c, k = self.parse_key(key)
        
        if self.config_parser.has_option(c, k):
            return self.config_parser.get(c, k)
        elif key in DEFAULTS:
            return str(DEFAULTS[key])
    
    def get_float(self, key):
        c, k = self.parse_key(key)
        
        if self.config_parser.has_option(c, k):
            return self.config_parser.getfloat(c, k)
        elif key in DEFAULTS:
            return float(DEFAULTS[key])

    def get_bool(self, key):
        c, k = self.parse_key(key)
        
        if self.config_parser.has_option(c, k):
            return self.config_parser.getboolean(c, k)
        elif key in DEFAULTS:
            return bool(DEFAULTS[key])
        
    def get_int(self, key):
        c, k = self.parse_key(key)
        
        if self.config_parser.has_option(c, k):
            return self.config_parser.getint(c, k)
        elif key in DEFAULTS:
            return int(DEFAULTS[key])
    
    def get_string_list(self, key):
        c, k = self.parse_key(key)
        
        if self.config_parser.has_option(c, k):
            a = self.config_parser.get(c, k)
            print a
            return list(a.split(", "))
        elif key in DEFAULTS:
            return list(DEFAULTS[key])
        
    def notify_add(self, key, func):
        pass #TODO: Write-me

class GConfClient:
    def __init__(self):
        self.gconf_client = GConf.Client.get_default()
        self.gconf_client.add_dir('/apps/%s' % APP_NAME,
                                  GConf.ClientPreloadType.PRELOAD_NONE)
    
    def parse_key(self, key):
        path = "/apps/%s/%s" % (APP_NAME,
                                key)
        return path
    
    def set_string(self, key, value):
        p = self.parse_key(key)
        self.gconf_client.set_string(p, value)
    
    def set_float(self, key, value):
        p = self.parse_key(key)
        self.gconf_client.set_float(p, value)
    
    def set_bool(self, key, value):
        p = self.parse_key(key)
        self.gconf_client.set_bool(p, value)
        
    def set_int(self, key, value):
        p = self.parse_key(key)
        self.gconf_client.set_int(p, value)
        
    def set_string_list(self, key, value):
        p = self.parse_key(key)
        self.gconf_client.set_list(p,
                                   GConf.ValueType.STRING,
                                   value)
        
    #Getters
    def get_string(self, key):
        p = self.parse_key(key)
        return self.gconf_client.get_string(p)

    def get_float(self, key):
        p = self.parse_key(key)
        return self.gconf_client.get_float(p)

    def get_bool(self, key):
        p = self.parse_key(key)
        return self.gconf_client.get_bool(p)

    def get_int(self, key):
        p = self.parse_key(key)
        return self.gconf_client.get_int(p)

    def get_string_list(self, key):
        p = self.parse_key(key)
        return self.gconf_client.get_list(p,
                                          GConf.ValueType.STRING)
    
    def notify_add(self, key, func):
        p = self.parse_key(key)
        self.gconf_client.notify_add(p, func)

def config_init(appname, config_file, defaults):
    global APP_NAME
    global CONFIG_FILE
    global DEFAULTS
    global CONFIG_CLIENT

    APP_NAME = appname
    CONFIG_FILE = config_file
    DEFAULTS = defaults
    
    if HAS_GCONF and not(ospath.exists(config_file)):
        CONFIG_CLIENT = GConfClient()
    else:
        CONFIG_CLIENT = ConfClient()

def get_default_client():
    
    return CONFIG_CLIENT
