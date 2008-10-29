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

## DBSession

(DB_TYPE_SQLITE,
 DB_TYPE_MYSQL,
 DB_TYPE_POSTGRES,
 DB_TYPE_ORACLE,
 DB_TYPE_MSSQL,
 DB_TYPE_FIREBIRD) = range(6)

DB_NAMES = [
    "sqlite",
    "mysql",
    "postgres",
    "oracle",
    "mssql",
    "firebird"
]
