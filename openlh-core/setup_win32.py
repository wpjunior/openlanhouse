#!/usr/bin/python
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

from distutils.core import setup, Extension

APP_VERSION = "0.2git"

certtool_ext = Extension(name           = "OpenlhCore.certtool",
                        sources        = ['src/certtool/template.c',
                                          'src/certtool/privkey.c',
                                          'src/certtool/self-signed.c',
                                          'src/certtool/certtool.c'],
                        include_dirs   = [],
                        library_dirs   = [],
                        libraries      = ['gcrypt', 'gnutls', 'gnutls-extra'])

config_in = open("src/OpenlhCore/config.py.in", "rb").read()
config_in = config_in.replace('@prefix@', '').replace("@VERSION@", APP_VERSION)

open("src/OpenlhCore/config.py", "wb").write(config_in)

setup(name = "openlh-core",
      version = APP_VERSION,
      author = "Wilson Pinto Júnior",
      author_email = "wilsonpjunior@gmail.com",
      url = "http://openlanhouse.org",
      download_url = "http://trac.openlanhouse.org/downloads",
      description = "Core lib for OpenLanhouse Server and Client",
      license = "GPLv3",
      platforms = ["Platform Independent"],
      ext_modules = [certtool_ext],
      package_dir = {'OpenlhCore': 'src/OpenlhCore'},
      packages = ('OpenlhCore', 'OpenlhCore.net',
                  'OpenlhCore.ui',
                  'OpenlhCore.net.backends',
                  'OpenlhCore.net.certgen'),
)

