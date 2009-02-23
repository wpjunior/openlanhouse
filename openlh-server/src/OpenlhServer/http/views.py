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

import os

def get_background(request, machine_hash):
    """
    Get Background
    """
    machine_manager = request.daemon.machine_manager
    machine_category_manager = request.daemon.machine_category_manager
    
    cmd = machine_manager.get_all().filter_by(hash_id=machine_hash)
    result = cmd.all()
    
    if result:
        machine = result[0]
        
        if machine.category:
            cat = machine.category
            
            if cat.custom_background:
                value = cat.background_path
                
                if value and os.path.exists(value):
                    request.send_file(value)
                    return
    
    value = request.daemon.conf_client.get_string('background_path')

    if value and os.path.exists(value):
        request.send_file(value)

def get_logo(request, machine_hash):
    """
    Get Background
    """
    machine_manager = request.daemon.machine_manager
    machine_category_manager = request.daemon.machine_category_manager
    
    cmd = machine_manager.get_all().filter_by(hash_id=machine_hash)
    result = cmd.all()
    
    if result:
        machine = result[0]
        
        if machine.category:
            cat = machine.category
            
            if cat.custom_logo:
                value = cat.logo_path
                
                if value and os.path.exists(value):
                    request.send_file(value)
                    return
    
    value = request.daemon.conf_client.get_string('logo_path')

    if value and os.path.exists(value):
        request.send_file(value)

URLS = ((r'^/get_background/(?P<machine_id>\w{40})$', get_background),
        (r'^/get_logo/(?P<machine_id>\w{40})$', get_logo))
