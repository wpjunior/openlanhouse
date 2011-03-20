#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008-2011 Wilson Pinto Júnior <wilson@openlanhouse.org>
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

import gobject
from OpenlhServer.db.globals import *

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.interfaces import PoolListener
from OpenlhServer.db.models import Base

class SetTextFactory(PoolListener):
     def connect(self, dbapi_con, con_record):
         dbapi_con.text_factory = str 

class DBSession(gobject.GObject):
    def __init__(self, db_type, db_file=None, host=None,
                 user=None, password=None, port=None,
                 database=None,
                 echo=False,
                 auto_commit=False,
                 check_same_thread=True):
        
        self.__gobject_init__()
        self.db_type = db_type
        self.db_file = db_file
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.database = database
        self.auto_commit = auto_commit
        engine_kwargs = {'echo': echo}

        if db_type == DB_TYPE_SQLITE:
            if self.db_file:
                self.engine_str = "sqlite:///" + self.db_file + "?check_same_thread=False"
            else:
                self.engine_str = "sqlite://:memory:"

            engine_kwargs['listeners']=[SetTextFactory()]
        
        else:
            assert self.host, "host cannot be None"

            args = []
            
            args.append(DB_NAMES[self.db_type])
            args.append("://")

            if self.user and self.password:
                args.append("%s:%s" % (self.user, self.password))
                args.append("@")
            elif self.user:
                args.append(self.user)
                args.append("@")
            
            if self.host and self.port:
                args.append("%s:%s" % (self.host, self.port))
            else:
                args.append(self.host)
            
            if self.database:
                args.append("/")
                args.append(self.database)

            self.engine_str = "".join(args)
        
        self.engine = create_engine(self.engine_str, **engine_kwargs)

        #if self.db_type == DB_TYPE_SQLITE: #hack :-) text_factory is unicode cause serious problems
        #    self.engine.connect().connection.connection.text_factory = str

        self.session_maker = sessionmaker(bind=self.engine, autoflush=True)
        self.metadata = MetaData()
        self.session = self.session_maker()
    
    def commit(self):
        self.session.commit()

    def create_all(self):
        Base.metadata.create_all(self.engine)
        self.metadata.create_all(self.engine)
    
    def save(self, obj):
        self.session.add(obj)
        
    def __repr__(self):
        return "<DBSession(%s)>" % self.engine_str
