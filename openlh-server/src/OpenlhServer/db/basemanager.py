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
from sqlalchemy.sql import select, and_, delete, update

class BaseManager(gobject.GObject):
    
    __gsignals__ = {'insert': (gobject.SIGNAL_RUN_FIRST,
                               gobject.TYPE_NONE,
                               (gobject.TYPE_PYOBJECT,)),
                   
                    'update': (gobject.SIGNAL_RUN_FIRST,
                               gobject.TYPE_NONE,
                               (gobject.TYPE_PYOBJECT,)),

                    'delete': (gobject.SIGNAL_RUN_FIRST,
                                gobject.TYPE_NONE,
                               (gobject.TYPE_INT,)),
                    
                    'credit_update': (gobject.SIGNAL_RUN_FIRST, #For UsersManager
                                      gobject.TYPE_NONE,
                                      (gobject.TYPE_INT,
                                       gobject.TYPE_FLOAT)),
                   }
    
    def __init__(self, db_session, object_type):
        self.__gobject_init__()
        self.db_session = db_session
        self.object_type = object_type
    
    def get_all(self):
        return self.db_session.session.query(self.object_type)
    
    def insert(self, object):
        
        #if not(isinstance(object, self.object_type)):
        #    raise TypeError, "must be %s object" % self.object_type.__name__

        self.db_session.save(object)
        self.commit()
        self.emit("insert", object)
    
    def delete(self, object):
        if not(isinstance(object, self.object_type)):
            raise TypeError, "must be %s object" % self.object_type.__name__
        
        id = object.id
        self.db_session.session.delete(object)
        self.commit()
        self.emit("delete", id)
    
    def update(self, object):
        if not(isinstance(object, self.object_type)):
            raise TypeError, "must be %s object" % self.object_type.__name__

        self.commit()
        self.emit("update", object)
        
    def commit(self):
        if self.db_session.auto_commit:
            self.db_session.session.commit()

class BaseFlow(BaseManager):
    def get_days(self, year, month):
        
        s = select([self.object_type.day], 
              and_(self.object_type.year==year, self.object_type.month==month))
        
        days = []
        
        for day, in self.db_session.session.execute(s):
            if not day in days:
                days.append(day)
        
        return days
