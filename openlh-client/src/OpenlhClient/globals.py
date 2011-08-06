#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008-2009 Wilson Pinto Júnior <wilsonpjunior@gmail.com>
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import locale
import gettext

from os import path as ospath
from os import name as osname

from OpenlhClient.config import *

SHARE_PATH = ospath.join(PREFIX, 'share', 'OpenlhClient')
LOCALE_PATH = ospath.join(PREFIX, 'share', 'locale')

if INSTALLED:
    CUR_PATH = SHARE_PATH
else:
    _rootpath = ospath.join(ospath.dirname(__file__), '../../')
    _abspath = ospath.abspath(_rootpath)
    CUR_PATH = ospath.join(_abspath, 'data')

##Folder paths
UI_PATH = ospath.join(CUR_PATH, 'ui')
ICON_PATH = ospath.join(CUR_PATH, 'icons')
STATUS_ICON_PATH = ospath.join(ICON_PATH, 'status')


USER_PATH = ospath.expanduser('~')

CONFIG_PREFIX = ospath.join(USER_PATH, '.config')
CONFIG_PATH = ospath.join(CONFIG_PREFIX, 'OpenlhClient')
CONFIG_FILE = ospath.join(CONFIG_PATH, "openlh-client.ini")
CERTS_PATH = ospath.join(CONFIG_PATH, 'certs')
CACHE_PATH = ospath.join(CONFIG_PATH, 'cache')

DBUS_INTERFACE = 'org.gnome.OpenlhClient'
DBUS_PATH = '/org/gnome/OpenlhClient'

BACKGROUND_CACHE = ospath.join(CACHE_PATH, 'wallpaper')
LOGO_CACHE = ospath.join(CACHE_PATH, 'logo')

##CLIENT FILES
##CONFIG FILES
CONFIG_CLIENT = ospath.join(CONFIG_PATH, 'openlh-client.conf')
CLIENT_PID_FILE = ospath.join(CONFIG_PATH, 'openlh-client.lock')

##CLIENT TLS FILES
CLIENT_TLS_KEY = ospath.join(CERTS_PATH, 'openlh-client.key')
CLIENT_TLS_CERT = ospath.join(CERTS_PATH, 'openlh-client.cert')
CLIENT_TLS_TEMPLATE = ospath.join(CERTS_PATH, 'openlh-client.template')

##Icons
CLIENT_ICON_NAME = 'openlh-client'

##APP
APP_NAME = 'OpenLanhouse'
APP_SITE = 'http://openlanhouse.org'
APP_COPYRIGHT = 'OpenLanhouse - Copyright (c) 2007-2009'

I18N_APP = 'openlh-client'

##Internacionalize
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(I18N_APP, LOCALE_PATH)
gettext.textdomain(I18N_APP)

_ = gettext.gettext

language = locale.setlocale(locale.LC_ALL, '')
end = language.find('.')
language = language[:end]
##End internacionalize

##APP Proprerties
APP_COMMENTS = _('a Free LAN House Client')
CLIENT_APP_NAME = _('OpenLanHouse - Client')

MIN_NICK = 4
MAX_NICK = 20
MIN_PASSWORD = 5
MAX_PASSWORD = 32
PREVIEW_SIZE = 200

#PORT CONF
SERVER_PORT = 4558
MAX_CHUNK_SIZE = 10485760

#COLORS
COLOR_YELLOW = '#FCE94F'
COLOR_RED = '#EF2929'

APP_DOCS = ""

APP_AUTHORS = ('Wilson Pinto Júnior <wilsonpjunior@gmail.com>',)
APP_ARTISTS = ('Wilson Pinto Júnior <wilsonpjunior@gmail.com>',)


APP_CONTRIB = ('Bruno Gonçalves <bigbruno@gmail.com>',
               'Gabriel Falcão <gabriel@guake-terminal.org>',
               'Lincoln de Sousa <lincoln@guake-terminal.org>',
               'Gustavo Noronha Silva <gns@gnome.org>',
               'Og Maciel <ogmaciel@gnome.org>'
               )

APP_TRANSLATORS = {'pt_BR': ("Wilson Pinto Júnior <wilsonpjunior@gmail.com>\n"
                             "Vladimir Melo <vladimirmelo.psi@gmail.com>"),
                   'es_ES': "Pier Jose Gotta Perez <piegope@fslcol.org>"}

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
