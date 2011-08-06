#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008-2011 Wilson Pinto Júnior <wilsonpjunior@gmail.com>
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

from sqlalchemy import Column, Integer, String, Numeric, Text, Date, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Version(Base):

    __tablename__ = 'openlh_versions'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=25, assert_unicode=True, convert_unicode=True), nullable=False, unique=True)
    value = Column(String(length=40, assert_unicode=True, convert_unicode=True), nullable=False)

    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __repr__(self):
        return "<Version(%s, %s)" % (self.name, self.value)

class MachineCategory(Base):

    __tablename__ = "openlh_machine_category"

    id= Column(Integer, primary_key=True)
    name = Column(String(25, convert_unicode=True), nullable=False, unique=True)
    custom_logo = Column(Boolean, default=False)
    custom_background = Column(Boolean, default=False)
    logo_path = Column(String(100, convert_unicode=True), nullable=True)
    background_path = Column(String(100, convert_unicode=True), nullable=True)
    custom_price_hour = Column(Boolean, default=False)
    price_hour = Column(Float, default=0)

    def __repr__(self):
        return ("<MachineCategory(%s)>" % self.name)

class UserCategory(Base):

    __tablename__ = "openlh_user_category"

    id= Column(Integer, primary_key=True)
    name = Column(String(25, convert_unicode=True), nullable=False, unique=True)
    allow_login = Column(Boolean, default=True)
    custom_price_hour = Column(Boolean, default=False)
    price_hour = Column(Float, default=0)

    def __repr__(self):
        return ("<UserCategory(%s)>" % self.name)

class User(Base):

    __tablename__ = "openlh_users"

    id = Column(Integer, primary_key=True)
    nick = Column(String(20, convert_unicode=True), nullable=False, unique=True)
    full_name = Column(String(50, convert_unicode=True), nullable=False)
    email = Column(String(50, convert_unicode=True))

    responsible = Column(String(50, convert_unicode=True))
    identity = Column(String(50, convert_unicode=True))
    birth = Column(String(10, convert_unicode=True)) #CHANGE TO DATE FORMAT
    city = Column(String(50, convert_unicode=True))
    state = Column(String(50, convert_unicode=True))
    phone = Column(String(50, convert_unicode=True))
    notes = Column(Text(convert_unicode=True))

    address = Column(Text(convert_unicode=True))
    last_login = Column(DateTime)
    last_machine_id = Column(Integer) ##bug circular dependency, ForeignKey('openlh_machines.id'))
    #last_machine = relation(Machine) 

    active = Column(Boolean, default=True)
    reg_date = Column(DateTime)
    login_count = Column(Integer, default=0)
    credit = Column(Float, default=0)
    password = Column(String(32, convert_unicode=True), nullable=False)

    category_id = Column(Integer, ForeignKey('openlh_user_category.id'))
    category = relation(UserCategory)

    def __init__(self, nick, full_name, password, *args, **kwargs):
        self.nick, self.full_name = nick, full_name
        self.password = password
    
    def __repr__(self):
        return "<User(%s, %s)>" % (self.nick, self.full_name)

class Machine(Base):

    __tablename__ = "openlh_machines"

    id = Column(Integer, primary_key=True)
    name = Column(String(25, convert_unicode=True), nullable=False, unique=True)
    hash_id = Column(String(40, convert_unicode=True), nullable=False)
    description = Column(Text(convert_unicode=True))
    last_user_id = Column('last_user_id', Integer, ForeignKey('openlh_users.id'))
    last_user = relation(User)
    category_id = Column(Integer, ForeignKey('openlh_machine_category.id'))
    category = relation(MachineCategory)

class CashFlowItem(Base):

    __tablename__ = "openlh_cash_flow"

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)

    user_id = Column(Integer, ForeignKey('openlh_users.id'))
    user = relation(User)

    value = Column(Float, nullable=False) #TODO: Change to real Type
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    hour = Column(String(8, convert_unicode=True), nullable=False)
    notes = Column(Text(convert_unicode=True))

class OpenDebtMachineItem(Base):

    __tablename__ = "openlh_opendebts_machine"
    
    id = Column(Integer, primary_key=True)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year= Column(Integer, nullable=False)
    machine_id = Column(Integer, ForeignKey('openlh_machines.id'))
    machine = relation(Machine)

    start_time = Column(String(8, convert_unicode=True), nullable=False)
    end_time = Column(String(8, convert_unicode=True), nullable=False)
    user_id = Column(Integer, ForeignKey('openlh_users.id'))
    user = relation(User)

    value = Column(Float, nullable=False) #TODO: Change to real Type
    notes = Column(Text(convert_unicode=True))
        
    def __repr__(self):
        return "<OpenDebtMachineItem(%0.2f)>" % self.value

class OpenDebtOtherItem(Base):

    __tablename__ = "openlh_opendebts_other"
    
    id = Column(Integer, primary_key=True)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year= Column(Integer, nullable=False)

    start_time = Column(String(8, convert_unicode=True), nullable=False)
    end_time = Column(String(8, convert_unicode=True), nullable=False)
    user_id = Column(Integer, ForeignKey('openlh_users.id'))
    user = relation(User)

    value = Column(Float, nullable=False) #TODO: Change to real Type
    notes = Column(Text(convert_unicode=True))
        
    def __repr__(self):
        return "<OpenDebtOtherItem(%0.2f)>" % self.value

class HistoryItem(Base):

    __tablename__ = "openlh_history"
    
    id = Column(Integer, primary_key=True)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    machine_id = Column(Integer, ForeignKey('openlh_machines.id'))
    time = Column(String(8, convert_unicode=True), nullable=False)
    start_time = Column(String(8, convert_unicode=True), nullable=False)
    end_time = Column(String(8, convert_unicode=True), nullable=False)
    user_id = Column(Integer, ForeignKey('openlh_users.id'))
    user = relation(User)
    machine = relation(Machine)
        
    def __repr__(self):
        return "<HistoryItem(%d)" % self.id

class OpenTicket(Base):
    __tablename__ = "openlh_open_tickets"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(25, convert_unicode=True), nullable=False, unique=True)
    price = Column(Float, nullable=False)
    hourly_rate = Column(Float, nullable=False)
    notes = Column(Text(convert_unicode=True))

    def __repr__(self):
        return "<OpenTicket(code=%s, price=%0.2f)>" % (self.code,
                                                       self.price)

if __name__ == '__main__':
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from datetime import date

    engine = create_engine('sqlite:///:memory:', echo=True)
    engine.connect().connection.connection.text_factory = str
    Session = sessionmaker(bind=engine)

    # Creates all database tables
    Version.metadata.create_all(engine)
    session = Session()
    dt = date.today()

    c = MachineCategory()
    c.name = "Macumba"
    
    m = Machine()
    m.name = "oi"
    m.hash_id = "jkasdjflasjdfaksdjfçlakdfjçalsdfkj"
    m.category = c
    session.add(m)
    session.commit()

    # Create a new Bill record
    ht = Version('Wilson Júnior', "0.2b")

    # Session to talk to the database
    session = Session()
    # Add new record to database
    session.add(ht)
    # Commit it
    session.commit()

    # Get all Bill records
    for instance in session.query(Version):
        print "Name %s version %s" % (instance.name, instance.value)

