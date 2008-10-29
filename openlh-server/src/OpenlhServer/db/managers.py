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

from OpenlhServer.db.models import Machine, User, CashFlowItem, HistoryItem
from OpenlhServer.db.models import OpenDebtMachineItem, OpenDebtOtherItem, Version
from OpenlhServer.db.basemanager import BaseManager, BaseFlow

from sqlalchemy import Table, Column, Boolean, Integer, String, Text
from sqlalchemy import Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import mapper, relation
from sqlalchemy.sql import select, and_, delete, update

class VersionManager(BaseManager):
    __table_name__ = "openlh_versions"
    
    def __init__(self, db_session):
        
        BaseManager.__init__(self, db_session, Version)
        
        self.table = Table(self.__table_name__,
                      self.db_session.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String(25), nullable=False, unique=True),
                      Column('value', String(40), nullable=False)
                      )
        
        self.mapper = mapper(Version, self.table)

class MachineManager(BaseManager):

    __table_name__ = "openlh_machines"
    
    def __init__(self, db_session):
        
        BaseManager.__init__(self, db_session, Machine)
        
        self.table = Table(self.__table_name__,
                      self.db_session.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String(25), nullable=False, unique=True),
                      Column('hash_id', String(40), nullable=False),
                      Column('description', Text),
                      Column('last_user_id', Integer, ForeignKey('openlh_users.id')),
                      )
        
        self.mapper = mapper(Machine, self.table,
                      properties={'last_user':relation(User)
                      })
    
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
    
    def get_last_user_id(self, id):
        s = select([Machine.last_user_id], Machine.id==id)
        out = self.db_session.session.execute(s).fetchone()
        
        if out:
            out = out[0]
        
        return out

class UserManager(BaseManager):
    
    __table_name__ = "openlh_users"
    
    def __init__(self, db_session):
        BaseManager.__init__(self, db_session, User)
        
        self.table = Table(self.__table_name__,
                      self.db_session.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('nick', String(20), nullable=False, unique=True),
                      Column('full_name', String(50), nullable=False),
                      Column('email', String(50)),
                      Column('responsible', String(50)),
                      Column('identity', String(50)),
                      Column('birth', String(10)), #CHANGE TO DATE FORMAT
                      Column('city', String(50)),
                      Column('state', String(50)),
                      Column('phone', String(50)),
                      Column('notes', Text),
                      Column('address', Text),
                      Column('last_login', DateTime),
                      Column('last_machine_id', Integer), #ForeignKey('openlh_machines.id')),
                      Column('active', Boolean, default=True),
                      Column('reg_date', DateTime),
                      Column('login_count', Integer, default=0),
                      Column('credit', Float, default=0),
                      Column('password', String(32), nullable=False),
                      )

        self.db_session = db_session
        self.mapper = mapper(User, self.table)
    
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
    
    __table_name__ = "openlh_cash_flow"
     
    def __init__(self, db_session):
        BaseFlow.__init__(self, db_session, CashFlowItem)

        self.table = Table(self.__table_name__,
                           self.db_session.metadata,
                           Column('id', Integer, primary_key=True),
                           Column('type', Integer, nullable=False),
                           Column('user_id', Integer, ForeignKey('openlh_users.id')),
                           Column('value', Float, nullable=False), #TODO: Change to real Type
                           Column('day', Integer, nullable=False),
                           Column('month', Integer, nullable=False),
                           Column('year', Integer, nullable=False),
                           Column('hour', String(8), nullable=False),
                           Column('notes', Text)
                          )
        
        self.mapper = mapper(CashFlowItem, self.table, 
                      properties={'user':relation(User)
                      })
    
class OpenDebtsMachineManager(BaseFlow):
    
    __table_name__ = "openlh_opendebts_machine"
     
    def __init__(self, db_session):
        BaseFlow.__init__(self, db_session, OpenDebtMachineItem)

        self.table = Table(self.__table_name__,
                           self.db_session.metadata,
                           Column('id', Integer, primary_key=True),
                           Column('day', Integer, nullable=False),
                           Column('month', Integer, nullable=False),
                           Column('year', Integer, nullable=False),
                           Column('machine_id', Integer, ForeignKey('openlh_machines.id')),
                           Column('start_time', String(8), nullable=False),
                           Column('end_time', String(8), nullable=False),
                           Column('user_id', Integer, ForeignKey('openlh_users.id')),
                           Column('value', Float, nullable=False), #TODO: Change to real Type
                           Column('notes', Text)
                          )
        
        self.mapper = mapper(OpenDebtMachineItem, self.table, 
                        properties={'user':relation(User),
                                    'machine':relation(Machine)})

class OpenDebtsOtherManager(BaseFlow):
    
    __table_name__ = "openlh_opendebts_other"
     
    def __init__(self, db_session):
        BaseFlow.__init__(self, db_session, OpenDebtOtherItem)

        self.table = Table(self.__table_name__,
                           self.db_session.metadata,
                           Column('id', Integer, primary_key=True),
                           Column('day', Integer, nullable=False),
                           Column('month', Integer, nullable=False),
                           Column('year', Integer, nullable=False),
                           Column('time', String(8), nullable=False),
                           Column('start_time', String(8), nullable=False),
                           Column('end_time', String(8), nullable=False),
                           Column('user_id', Integer, ForeignKey('openlh_users.id')),
                           Column('value', Float, nullable=False), #TODO: Change to real Type
                           Column('notes', Text)
                          )
        
        self.mapper = mapper(OpenDebtOtherItem, self.table, 
                        properties={'user':relation(User)})


class HistoryManager(BaseFlow):
    __table_name__ = "openlh_history"
     
    def __init__(self, db_session):
        BaseFlow.__init__(self, db_session, HistoryItem)

        self.table = Table(self.__table_name__,
                           self.db_session.metadata,
                           Column('id', Integer, primary_key=True),
                           Column('day', Integer, nullable=False),
                           Column('month', Integer, nullable=False),
                           Column('year', Integer, nullable=False),
                           Column('machine_id', Integer, ForeignKey('openlh_machines.id')),
                           Column('time', String(8), nullable=False),
                           Column('start_time', String(8), nullable=False),
                           Column('end_time', String(8), nullable=False),
                           Column('user_id', Integer, ForeignKey('openlh_users.id')),
                          )
        
        self.mapper = mapper(HistoryItem, self.table, 
                        properties={'user':relation(User),
                                    'machine':relation(Machine)})
    
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