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

class Machine(object):
    __name__ = "Machine"
    def __repr__(self):
        return ("<Machine(name=%s hash_id=%s)>" % \
                        (self.name, self.hash_id))

class MachineCategory(object):
    __name__ = "MachineCategory"
    def __repr__(self):
        return ("<CategoryMachine(%s)>" % self.name)

class UserCategory(object):
    __name__ = "UserCategory"
    def __repr__(self):
        return ("<UserMachine(%s)>" % self.name)

class CashFlowItem(object):
    __name__ = "CashFlowItem"
    def __repr__(self):
        return "<CashFlowItem(%0.2f)>" % self.value

class OpenDebtMachineItem(object):
    __name__ = "OpenDebtMachineItem"
    def __repr__(self):
        return "<OpenDebtMachineItem(%0.2f)>" % self.value

class OpenDebtOtherItem(object):
    __name__ = "OpenDebtOtherItem"
    def __repr__(self):
        return "<OpenDebtOtherItem(%0.2f)>" % self.value

class HistoryItem(object):
    __name__ = "HistoryItem"

class User(object):
    __name__ = "User"
    
    (nick, full_name, email, responsible, identity, birth,
     city, state, phone, notes, address, last_login,
     last_machine, reg_date, password) = (None,) * 15
    
    active = True
    credit = 0
    login_count = 0

    def __init__(self, nick, full_name, password, *args, **kwargs):
        self.nick, self.full_name = nick, full_name
        self.password = password
    
    def __repr__(self):
        return "<User(%s, %s)>" % (self.nick, self.full_name)

class Version(object):
    __name__ = "Version"
    
    name, value = None, None
    
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __repr__(self):
        return "<Version(%s, %s)" % (self.name, self.value)

class OpenTicket(object):
    __name__ = "OpenTicket"
    
    def __repr__(self):
        return "<OpenTicket(code=%s, price=%0.2f)>" % (self.code,
                                                       self.price)
