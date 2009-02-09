#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008-2009 Wilson Pinto Júnior <wilson@openlanhouse.org>
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

def get_background(request, machine_hash):
    print request, machine_hash
    return "/media/sda5/Wallpapers/Debian GNU.jpg"

def get_logo(request):
    request.send_file("/media/sda5/Wallpapers/Debian GNU.jpg")

URLS = ((r'^/get_background/(?P<machine_id>\w{40})$', get_background),
        (r'^/get_logo$', get_logo))
