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

import re

XMLRESPONSE_TYPE, XMLREQUEST_TYPE, SENDFILE_TYPE = range(1, 4)

BEGIN_XMLRESPONSE_HEADER = '-----BEGIN XMLRESPONSE ID=%d SIZE=%d-----'
END_XMLRESPONSE_HEADER = '-----END XMLRESPONSE-----'

BEGIN_XMLREQUEST_HEADER = "-----BEGIN XMLREQUEST ID=%d SIZE=%d-----"
END_XMLREQUEST_HEADER = "-----END XMLREQUEST-----"

BEGIN_SENDFILE_HEADER = "-----BEGIN SENDFILE ID=%d METHOD=%s SIZE=%d-----"
END_SENDFILE_HEADER = "-----END SENDFILE-----"

HASH_ID_HEADER = '-----HASH_ID=%s-----'

HashIDRegex = re.compile(r'-----HASH_ID=(?P<hash_id>\w+)-----(?P<data>(.*))')

XMLResponseRegex = re.compile(r'-----BEGIN XMLRESPONSE ID=(?P<id>\d+)'
                              r' SIZE=(?P<size>\d+)-----(?P<data>(.*))')

XMLRequestRegex = re.compile(r'-----BEGIN XMLREQUEST'
                             r' ID=(?P<id>\d+) SIZE=(?P<size>\d+)-----(?P<data>(.*))')

SendFileRegex = re.compile(r'-----BEGIN SENDFILE ID=(?P<id>\d+) METHOD=(?P<method>[\w._]+) '
                           r'SIZE=(?P<size>\d+)-----(?P<data>(.*))')