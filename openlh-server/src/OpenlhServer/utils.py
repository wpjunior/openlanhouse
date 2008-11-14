#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2007-2008 Wilson Pinto Júnior <wilson@openlanhouse.org>
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

import os
import sys
import random

from OpenlhServer.globals import AVATARS_PATH

def get_user_avatar_path(user_id):
    """
        Get the avatar path for the user
    """
    return os.path.join(AVATARS_PATH, "%d.png" % user_id)

def user_has_avatar(user_id):
    return os.path.exists(get_user_avatar_path(user_id))

# Ticket Generator
TICKET_VALID_CARACTERS = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                   'I', 'K', 'J', 'L', 'M','N', 'O', 'P', 'Q',
                   'R', 'S', 'T', 'U', 'V', 'X', 'W', 'Y', 'Z',
                   '0', '1', '2', '3', '4', '5', '6', '7', '8',
                   '9')

TICKET_VALID_CARACTERS_RANGE = len(TICKET_VALID_CARACTERS) -1

def random_caracter():
    c = random.randint(0, TICKET_VALID_CARACTERS_RANGE)
    return TICKET_VALID_CARACTERS[c]

def generate_ticket(size):
    ticket = []
    for i in range(size):
        ticket.append(random_caracter())

    ticket = "".join(ticket)
                
    return ticket

