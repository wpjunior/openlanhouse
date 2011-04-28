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

from OpenlhServer.db.models import Machine, User, CashFlowItem, HistoryItem, MachineCategory
from OpenlhServer.db.models import OpenDebtMachineItem, OpenDebtOtherItem, Version, UserCategory
from OpenlhServer.db.models import OpenTicket
from OpenlhServer.db.basemanager import BaseManager, BaseFlow

from sqlalchemy import Table, Column, Boolean, Integer, String, Text
from sqlalchemy import Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import mapper, relation
from sqlalchemy.sql import select, and_, delete, update

class VersionManager(BaseManager):
    def __init__(self, db_session):
        BaseManager.__init__(self, db_session, Version)

class MachineCategoryManager(BaseManager):
    def __init__(self, db_session):
        BaseManager.__init__(self, db_session, MachineCategory)

class UserCategoryManager(BaseManager):
    def __init__(self, db_session):
        BaseManager.__init__(self, db_session, UserCategory)

class MachineManager(BaseManager):
    def __init__(self, db_session):
        BaseManager.__init__(self, db_session, Machine)
    
    def delete_by_id(self, id):
        s = delete(self.table, Machine.id==id)
        self.db_session.session.execute(s)
        self.commit()
        self.emit("delete", id)
    
    def get_name(self, id):
        s = select([Machine.name], Machine.id==id)
        out = self.db_session.session.execute(s).fetchone()
        
        if out:
            out = out[0]
        
        return out

    def get_machines_id_by_category_id(self, category_id):
        s = select([Machine.id], Machine.category_id==category_id)
        return self.db_session.session.execute(s).fetchall()
    
    def get_last_user_id(self, id):
        s = select([Machine.last_user_id], Machine.id==id)
        out = self.db_session.session.execute(s).fetchone()
        
        if out:
            out = out[0]
        
        return out

class UserManager(BaseManager):
    def __init__(self, db_session):
        BaseManager.__init__(self, db_session, User)
    
    def get_full_name(self, user_id):
        
        s = select([User.full_name], User.id==user_id)
        out = self.db_session.session.execute(s).fetchone()
        
        if out:
            full_name, = out
            return full_name
    
    def get_full_name_and_nick(self):
        s = select([User.full_name, User.nick])
        return self.db_session.session.execute(s)
    
    def get_credit(self, condition, value):
        s = select([User.credit], condition==value)
        out = self.db_session.session.execute(s).fetchone()
        
        if out:
            out = out[0]
        
        return out
    
    def get_credit_and_id(self, user_nick):
        s = select([User.credit, User.id], User.nick==user_nick)
        return self.db_session.session.execute(s).fetchone()
    
    def get_full_name_and_credit(self, user_id):
        s = select([User.full_name, User.credit], User.id==user_id)
        return self.db_session.session.execute(s).fetchone()
    
    def update_credit(self, user_id, value):
        s = update(self.table, User.id==user_id, {'credit': value})
        self.db_session.session.execute(s)
        self.commit()
        self.emit('credit_update', user_id, value)
    
    def change_password(self, user_id, password):
        s = update(self.table, User.id==user_id, {'password': password})
        self.db_session.session.execute(s)
        self.commit()
        
    def check_user(self, user_nick, password):
        s = select([User.id, User.credit], 
                    and_(User.nick==user_nick, 
                         User.password==password, 
                         User.active==True))
        return self.db_session.session.execute(s).fetchone()

class CashFlowManager(BaseFlow):
    def __init__(self, db_session):
        BaseFlow.__init__(self, db_session, CashFlowItem)
    
class OpenDebtsMachineManager(BaseFlow):
    def __init__(self, db_session):
        BaseFlow.__init__(self, db_session, OpenDebtMachineItem)

class OpenDebtsOtherManager(BaseFlow):
    def __init__(self, db_session):
        BaseFlow.__init__(self, db_session, OpenDebtOtherItem)


class HistoryManager(BaseFlow):
    __table_name__ = "openlh_history"
     
    def __init__(self, db_session):
        BaseFlow.__init__(self, db_session, HistoryItem)
    
    def get_days_for_machine_id(self, year, month, machine_id):
        s = select([HistoryItem.day], 
              and_(HistoryItem.year==year, 
                   HistoryItem.month==month,
                   HistoryItem.machine_id==machine_id))
        
        days = []
        
        for day, in self.db_session.session.execute(s):
            if not day in days:
                days.append(day)
        
        return days
    
    def clear_all(self):
        s = delete(self.table)
        self.db_session.session.execute(s)
        self.commit()
    
    def clear_by_year(self, year):
        s = delete(self.table, HistoryItem.year==year)
        self.db_session.session.execute(s)
        self.commit()
    
    def clear_by_year_and_month(self, year, month):
        s = delete(self.table, 
                   and_(HistoryItem.year==year, HistoryItem.month==month))
        self.db_session.session.execute(s)
        self.commit()

class OpenTicketManager(BaseManager):
    def __init__(self, db_session):
        BaseManager.__init__(self, db_session, OpenTicket)
        
    def ticket_exists(self, code):
        s = select([OpenTicket.id], OpenTicket.code==code)
        return bool(self.db_session.session.execute(s).fetchone())
