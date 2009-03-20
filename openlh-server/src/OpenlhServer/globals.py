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

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import locale
import gettext

from os import path as ospath
from os import name as osname
from OpenlhServer.config import *

SHARE_PATH = ospath.join(PREFIX, 'share', 'OpenlhServer')
LOCALE_PATH = ospath.join(PREFIX, 'share', 'locale')

if INSTALLED:
    CUR_PATH = SHARE_PATH
else:
    _rootpath = ospath.join(ospath.dirname(__file__), '../../')
    _abspath = ospath.abspath(_rootpath)
    CUR_PATH = ospath.join(_abspath, 'data')

##Folder paths
ICON_PATH = ospath.join(CUR_PATH, 'icons')
STATUS_ICON_PATH = ospath.join(ICON_PATH, 'status')

USER_PATH = ospath.expanduser('~')

I_AM_DEVELOPER_FILE = ospath.join(USER_PATH, ".openlanhouse_developer")
CONFIG_PREFIX = ospath.join(USER_PATH, '.config')
CONFIG_PATH = ospath.join(CONFIG_PREFIX, 'OpenlhServer')
CONFIG_FILE = ospath.join(CONFIG_PATH, 'openlh-server.ini')
CERTS_PATH = ospath.join(CONFIG_PATH, 'certs')
UI_PATH = ospath.join(CUR_PATH, 'ui')
CACHE_PATH = ospath.join(CONFIG_PATH, 'cache')
AVATARS_PATH = ospath.join(CONFIG_PATH, 'avatars')
BACKGROUND_CACHE = ospath.join(CACHE_PATH, 'wallpaper')
LOGO_CACHE = ospath.join(CACHE_PATH, 'logo')

##SERVER TLS FILES
SERVER_TLS_KEY = ospath.join(CERTS_PATH, 'openlh-server.key')
SERVER_TLS_CERT = ospath.join(CERTS_PATH, 'openlh-server.cert')
SERVER_TLS_TEMPLATE = ospath.join(CERTS_PATH, 'openlh-server.template')

##DB FILES
SQLITE_FILE = ospath.join(CONFIG_PATH, 'database.db')
SERVER_PID_FILE = ospath.join(CONFIG_PATH, 'openlh-server.lock')
REGISTRATION_DIR = ospath.join(CONFIG_PATH, 'registrations')

##Icons
SERVER_ICON_NAME = 'openlh-server'

(CASH_FLOW_TYPE_CREDIT_IN,
 CASH_FLOW_TYPE_CREDIT_OUT,
 CASH_FLOW_TYPE_MACHINE_USAGE_IN,
 CASH_FLOW_CUSTOM_TYPE_IN,
 CASH_FLOW_CUSTOM_TYPE_OUT,
 CASH_FLOW_TYPE_TICKET,
 CASH_FLOW_TYPE_TICKET_RETURN,
 CASH_FLOW_TYPE_MACHINE_PRE_PAID,
 CASH_FLOW_TYPE_DEBT_PAID) = range(9)

CASH_FLOW_TYPE_IN = (CASH_FLOW_TYPE_CREDIT_IN, CASH_FLOW_TYPE_MACHINE_USAGE_IN, CASH_FLOW_CUSTOM_TYPE_IN,
                     CASH_FLOW_TYPE_TICKET, CASH_FLOW_TYPE_MACHINE_PRE_PAID)

MACHINE_STATUS_OFFLINE = 0
MACHINE_STATUS_AVAIL = 1
MACHINE_STATUS_BUSY = 2
MACHINE_STATUS_AWAY = 3

##APP
APP_NAME = 'OpenLanhouse'
APP_SITE = 'http://openlanhouse.org'
APP_COPYRIGHT = 'OpenLanhouse - Copyright (c) 2007-2009'

I18N_APP = 'openlh-server'

##Internacionalize
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(I18N_APP, LOCALE_PATH)
gettext.textdomain(I18N_APP)

global _
_ = gettext.gettext
language = locale.setlocale(locale.LC_ALL, '')
end = language.find('.')
language = language[:end]
##End internacionalize

##APP Proprerties
APP_COMMENTS = _('a Free LAN House Manager')
CLIENT_APP_NAME = _('OpenLanHouse - Client')
MANAGER_APP_NAME = _('OpenLanHouse - Administration')

MIN_NICK = 4
MAX_NICK = 18
PREVIEW_SIZE = 200

#PORT CONF
SERVER_PORT = 4558
MAX_CHUNK_SIZE = 10485760

#COLORS
COLOR_YELLOW = '#FCE94F'
COLOR_RED = '#EF2929'

##DATA FILES

APP_DOCS = ""

APP_AUTHORS = ('Wilson Pinto Júnior <wilson@openlanhouse.org>',)
APP_ARTISTS = ('Wilson Pinto Júnior <wilson@openlanhouse.org>',)


APP_CONTRIB = ('Bruno Gonçalves <bigbruno@gmail.com>',
               'Gabriel Falcão <gabriel@guake-terminal.org>',
               'Lincoln de Sousa <lincoln@guake-terminal.org>',
               'Gustavo Noronha Silva <gns@gnome.org>',
               'Og Maciel <ogmaciel@gnome.org>'
               )

APP_LICENCE = _('OpenLanhouse is free software: you can redistribute it and/or modify\n'
                'it under the terms of the GNU General Public License as published by\n'
                'the Free Software Foundation, either version 3 of the License, or\n'
                '(at your option) any later version.\n\n'
                'This program is distributed in the hope that it will be useful,\n'
                'but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
                'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'
                'GNU General Public License for more details.\n\n'
                'You should have received a copy of the GNU General Public License\n'
                'along with this program.  If not, see <http://www.gnu.org/licenses/>.'
                )

WIKI_URL = "http://trac.openlanhouse.org/wiki"
DONATION_URL = "http://trac.openlanhouse.org/wiki/donation"
HELP_HASHID_URL = "http://trac.openlanhouse.org/wiki/hash_id"
