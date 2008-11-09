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

import sys
import os
import logging
import gobject
import time
import datetime

from OpenlhCore.net.server import NetServer
from OpenlhCore.net.request_handler import RequestHandler
from OpenlhCore.ConfigClient import get_default_client

from OpenlhServer.globals import *
from OpenlhServer.ui import dialogs
from OpenlhCore.utils import threaded, md5_cripto, humanize_time
from OpenlhServer.g_timer import TimerManager, TimeredObj

from OpenlhServer.plugins import get_plugin

from OpenlhServer.db.models import Machine, User, OpenDebtMachineItem, HistoryItem, Version
from OpenlhServer.db.session import DBSession
from OpenlhServer.db.managers import MachineManager, UserManager, CashFlowManager
from OpenlhServer.db.managers import OpenDebtsMachineManager, OpenDebtsOtherManager
from OpenlhServer.db.managers import HistoryManager, VersionManager, MachineCategoryManager, UserCategoryManager
from OpenlhServer.db.globals import DB_NAMES

_ = gettext.gettext

class MachineInst(gobject.GObject):
    """
        Class used for each machine registred
    """
    
    id = None
    name = None
    hash_id = None
    description = None
    category_id = 0
    session = None
    manager = None
    user_id = None
    source = None
    status = MACHINE_STATUS_OFFLINE
    
    limited = False
    time = None
    registred = False
    last_consume_credit = None
    total_to_pay = 0.0
    price_per_hour = 0
    consume_handler_id = 0
    consume_credit_update_interval = 30000
    start_time = None
    mstart_time = None
    
    def __init__(self, manager, id, name, hash_id, description, category_id):
        self.__gobject_init__()
        
        self.manager = manager
        
        self.timer_obj = TimeredObj()
        self.timer_obj._name = name
        self.timer_obj.connect("done", self.time_done)
        
        self.id = id
        self.name = name
        self.hash_id = hash_id
        self.description = description
        self.category_id = category_id
    
    def set_connected(self, session):
        """
            Set machine instance connected
        """
        self.status = MACHINE_STATUS_AVAIL
        self.session = session
        self.source = session.client_address[0]
        self.send_myinfo()
    
    def send_myinfo(self):
        """
            Send Basic Machine Information
        """
        if self.session:
            self.session.request('main.set_myinfo', 
                                 {'id':self.id, 'name':self.name,
                                  'description':self.description})
            return True
        return False
    
    def set_disconnected(self):
        """
            Set machine instance disconnected
        """
        if self.consume_handler_id:
            gobject.source_remove(self.consume_handler_id)
        
        #If busy, write an entry on history
        if self.status == MACHINE_STATUS_BUSY:
            tt_time = "%0.2d:%0.2d:%0.2d" % humanize_time(time.time() - self.mstart_time)
            
            hitem = HistoryItem()
            hitem.year = self.start_time.year
            hitem.month = self.start_time.month
            hitem.day = self.start_time.day
            hitem.time = tt_time
            hitem.start_time = self.start_time.strftime(_("%H:%M:%S"))
            hitem.end_time = time.strftime(_("%H:%M:%S"))
            hitem.user_id = self.user_id
            hitem.machine_id = self.id
            
            self.manager.server.history_manager.insert(hitem)
        
        self.status = MACHINE_STATUS_OFFLINE
        self.session = None
        self.source = None
    
    @threaded
    def set_background(self, background_path):
        """
            Set machine background
        """
        if self.session:
            self.session.send_file('main.set_background', background_path)
            return True
        else:
            return False
    
    @threaded
    def set_logo(self, logo_path):
        """
            Set machine logo
        """
        if self.session:
            self.session.send_file('main.set_logo', logo_path)
            return True
        else:
            return False
    
    def send_information(self, data):
        """
            Send information to machine, data must be a dict
        """
        if self.session:
            self.session.request("core.set_information", (data,))
            return True
        else:
            return False
    
    def unblock(self, registred, limited, user_id, machine_time, price_per_hour):
        """
            Unblock machine
            @registred:
                case True, user may be registred
            @limited:
                case True, time may be limited
            @user_id:
                user id used for registred mode
            @machine_time:
                Time used for limited mode
            @price_per_hour:
                Price per hour
        """
        if self.session:
            self.price_per_hour = price_per_hour
            self.last_consume_credit = int(time.time())
            self.consume_credit_update_interval = int(36000 / self.price_per_hour) #36000 = (0.01 * 60 * 60 * 1000) 
            self.consume_handler_id = gobject.timeout_add(
                                self.consume_credit_update_interval,
                                self.consume_credits)
            
            self.status = MACHINE_STATUS_BUSY
            self.registred = registred
            self.limited = limited
            self.user_id = user_id
            self.time = machine_time
            self.total_to_pay = 0.0
            self.start_time = datetime.datetime.now()
            self.mstart_time = time.time()
           
            self.manager.emit("status_changed", self)
            
            data = {
                    'registred': registred,
                    'limited': limited
                    }
            
            if machine_time:
                data['time'] = machine_time
            
            self.session.request("core.unblock", data) #send unblock to machine
            
            machines_manager = self.manager.server.machine_manager
            m = machines_manager.get_all().filter_by(id=self.id).one() #
            
            if registred:
                m.last_user_id = user_id
                users_manager = self.manager.server.users_manager
                full_name, credit = users_manager.get_full_name_and_credit(user_id)
                self.session.request(
                    'set_status', {'credit': credit, 'full_name': full_name})
            else:
                m.last_user_id = 0 #Isso pode causar bugs ?!?
            
            machines_manager.update(m)
            return True
        else:
            return False
    
    def block(self, after, action):
        """
            Block machine
        """
        if self.session:
            self.price_per_hour = 0
            self.consume_credits() #cosume last credits
            
            if self.consume_handler_id:
                gobject.source_remove(self.consume_handler_id)
            
            tt_time = "%0.2d:%0.2d:%0.2d" % humanize_time(time.time() - self.mstart_time)
            
            if self.total_to_pay:
                oitem = OpenDebtMachineItem()
                oitem.year = self.start_time.year
                oitem.month = self.start_time.month
                oitem.day = self.start_time.day
                oitem.start_time = self.start_time.strftime(_("%H:%M:%S"))
                oitem.end_time = time.strftime(_("%H:%M:%S"))
                oitem.user_id = self.user_id
                oitem.machine_id = self.id
                oitem.value = self.total_to_pay
                
                self.manager.server.open_debts_machine_manager.insert(oitem)
            
            #History Item
            hitem = HistoryItem()
            hitem.year = self.start_time.year
            hitem.month = self.start_time.month
            hitem.day = self.start_time.day
            hitem.time = tt_time
            hitem.start_time = self.start_time.strftime(_("%H:%M:%S"))
            hitem.end_time = time.strftime(_("%H:%M:%S"))
            hitem.user_id = self.user_id
            hitem.machine_id = self.id
            
            self.manager.server.history_manager.insert(hitem)
            
            self.manager.timer_manager.remove_timered_obj(self.timer_obj)
            
            self.status = MACHINE_STATUS_AVAIL
            self.last_consume_credit = None
            self.user_id = None
            self.limited = False
            self.time = None
            self.registred = False
            self.total_to_pay = 0.0
            self.start_time = None
            self.mstart_time = None
            
            self.manager.emit("status_changed", self)
            self.session.request("core.block", (after, action)) #send block signal to machine
            return True
        else:
            return False
    
    def time_done(self, timered_obj):
        self.block(False, 0)
    
    def get_elapsed_time(self):
        return self.timer_obj.elapsed_time
    
    def consume_credits(self):
        self.consume_handler_id = gobject.timeout_add(
                            self.consume_credit_update_interval,
                            self.consume_credits)
        
        if not self.last_consume_credit:
            return
        
        d = int(time.time()) - self.last_consume_credit
        if not d:
            return
        
        total = (float(self.price_per_hour * d) / 60 / 60)
        self.last_consume_credit = int(time.time())
        
        if self.registred:
            self.manager.discount_credit(self, total)
        else:
            self.total_to_pay += total
            self.manager.update_total_to_pay(self, self.total_to_pay)
        
    def get_last_time(self):
        t = self.timer_obj._stop_time - self.timer_obj.elapsed_time
        return t

    def get_last_time_percentage(self):
        if self.timer_obj._stop_time:
            t = (float(self.timer_obj._stop_time -
                 self.timer_obj.elapsed_time) /
                 self.timer_obj._stop_time) * 100
            
            return t

    def get_time_elapsed_percentage(self):
        if self.timer_obj._stop_time:
            t = (float(self.timer_obj.elapsed_time) /
                 float(self.timer_obj._stop_time)) * 100

            return t

class InstManager(gobject.GObject):
    """
        Class used for manage MachineInst objects
    """
    
    __gsignals__ = {'new':(gobject.SIGNAL_RUN_FIRST,
                               gobject.TYPE_NONE,
                               (
                                gobject.TYPE_PYOBJECT,
                               )),
                    
                    'status_changed':(gobject.SIGNAL_RUN_FIRST,
                               gobject.TYPE_NONE,
                               (
                                gobject.TYPE_PYOBJECT,
                               )),
                    
                    'update':(gobject.SIGNAL_RUN_FIRST,
                               gobject.TYPE_NONE,
                               (
                                gobject.TYPE_PYOBJECT,
                               )),
                    
                    'update_total_to_pay':(gobject.SIGNAL_RUN_FIRST,
                               gobject.TYPE_NONE,
                               (
                                gobject.TYPE_PYOBJECT,
                                gobject.TYPE_FLOAT
                               )),
                    
                    'delete': (gobject.SIGNAL_RUN_FIRST,
                                gobject.TYPE_NONE,
                               (gobject.TYPE_STRING,)),
                    
                    }
    
    authorization_func = None
    machines_by_id = {}
    machines_by_hash_id = {}
    common_background = None
    common_logo = None
    common_logo_buffer = None
    
    def __init__(self, server, netserver, machine_manager,
                 machine_category_manager, users_manager):
        
        self.__gobject_init__()
        
        self.server = server
        self.netserver = netserver
        self.machine_manager = machine_manager
        self.machine_category_manager = machine_category_manager
        self.users_manager = users_manager
        
        self.logger = logging.getLogger('InstManager')
        self.conf_client = self.server.conf_client
        self.conf_client = self.server.conf_client
        self.timer_manager = TimerManager()
        
        #Get All Machine instances in database
        for machine in self.machine_manager.get_all():
            
            machineinst = MachineInst(self,
                                      id=machine.id,
                                      name=machine.name,
                                      hash_id=machine.hash_id,
                                      description=machine.description,
                                      category_id=machine.category_id)
            
            self.machines_by_id[machine.id] = machineinst
            self.machines_by_hash_id[machine.hash_id] = machineinst
        
        self.netserver.connect('connected', self.connected_machine)
        self.netserver.connect('disconnected', self.disconnected_machine)
        
        self.netserver.dispatch_func = self.dispatch_func
        self.netserver.recvfile_func = self.recvfile_func
        
    def get_status(self, machine_inst):
        """
            Get machine time status
        """
        data = {}
        
        data['limited'] = machine_inst.limited
        data['elapsed'] = machine_inst.get_elapsed_time()
        
        if data['limited']:
            data['time'] = machine_inst.time
            data['left_time'] = machine_inst.get_last_time()
        
        return data
        
    def send_background(self, machine_inst):
        if self.server.common_background:
            machine_inst.set_background(self.server.common_background)
        
        return True
    
    def send_logo(self, machine_inst):
        if self.server.common_logo:
            machine_inst.set_logo(self.server.common_logo)
        
        return True
    
    def dispatch_func(self, hash_id, method, params):
        
        machine_inst = self.machines_by_hash_id[hash_id]
        
        if method == "get_status":
            return self.get_status(machine_inst)
        
        elif method == "get_background":
            return self.send_background(machine_inst)
        
        elif method == "get_logo":
            return self.send_logo(machine_inst)
        
        elif method == "login":
            return self.machine_login(machine_inst, *params)
        
        elif method == "logout":
            return self.machine_logout(machine_inst)
        
        return True
        
    def recvfile_func(self, method, data):
        print method
        
    def allow_machine(self, hash_id, data, session):
        
        m = Machine()
        m.name = data['name']
        m.hash_id = hash_id
        m.description = data['description']
        m.category_id = data['category_id']
        
        self.machine_manager.insert(m)
        
        machineinst = MachineInst(self,
                                  id=m.id,
                                  name=m.name,
                                  hash_id=m.hash_id,
                                  description=m.description,
                                  category_id=m.category_id)
        
        self.machines_by_id[m.id] = machineinst
        self.machines_by_hash_id[m.hash_id] = machineinst
        
        if session:
            if not session.disconnected:
                machineinst.set_connected(session)
                machineinst.send_information(self.server.information)
        
        self.emit("new", machineinst)
        
    def connected_machine(self, obj, host, session, hash_id):
        """
            Network callback on machine is connected
        """
        if self.machine_manager.get_all().filter_by(hash_id=hash_id).count() == 1:
            
            machine = self.machines_by_hash_id[hash_id]
            machine.set_connected(session)
            machine.send_information(self.server.information)
            self.emit("status_changed", machine)
            
        else:
            if hash_id and self.authorization_func:
                self.authorization_func(hash_id, session)
            else:
                session.close_session()
    
    def delete_machine(self, machine_inst):
        id = machine_inst.id
        hash_id = machine_inst.hash_id
        self.machines_by_id.pop(id)
        self.machines_by_hash_id.pop(hash_id)
        self.machine_manager.delete_by_id(id)
        
        if machine_inst.session:
            machine_inst.session.close_session()
        
        self.emit("delete", hash_id)
    
    def update(self, machine_inst, data):
        machine_db_obj = self.machine_manager.get_all().filter_by(
                                            id=machine_inst.id).one()
        
        for key, value in data.items():
            setattr(machine_db_obj, key, value)
        
        self.machine_manager.update(machine_db_obj)
        
        if 'name' in data:
            machine_inst.name = data['name']
        
        if 'description' in data:
            machine_inst.description = data['description']
        
        if 'category_id' in data:
            machine_inst.category_id = data['category_id']
        
        machine_inst.send_myinfo()
        
        self.emit("update", machine_inst)
    
    def disconnected_machine(self, obj, host, hash_id):
        """
            Network callback on machine is disconnected
        """
        if hash_id in self.machines_by_hash_id:
            
            machine = self.machines_by_hash_id[hash_id]
            machine.set_disconnected()
            self.timer_manager.remove_timered_obj(machine.timer_obj)
            self.emit("status_changed", machine)
    
    def update_backgroud(self, background_path):
        """
            Send background to all machines
            @background_path:
                is a path to background image
        """
        
        self.logger.debug('Sending background to all machines')
        
        self.common_background = background_path
        
        for machine in self.machines_by_id.values():
            machine.set_background(self.common_background)
    
    def update_logo(self, logo_path):
        """
            Send logo to all machines
            @logo_path:
                is a path to logo image
        """
        
        self.logger.debug('Sending logo to all machines')
        
        self.common_logo = logo_path
        
        for machine in self.machines_by_id.values():
            machine.set_logo(self.common_logo)
    
    def update_information(self, data):
        """
            Send informations for all machines
            @data:
                dict containing informations
        """
        for machine in self.machines_by_id.values():
            machine.send_information(data)
    
    def unblock(self, machine_inst, registred, limited, 
                user_id, time, price_per_hour=None):
        """
            Unblock machine
            @machine_inst:
                MachineInst object representing a machine
            @registred:
                case True, unblock machine in registred mode, 
                if True user_id cannot be a None Value"
            @limited:
                case True, unblock machine in limited mode,
                if True, time cannot be a None Value
            @user_id:
                id for user used in registred mode
            @time:
                a tuple containing a hour and minute used for limited mode
        """
        
        if time:
            hour, minutes = time
            total_secs = (hour * 60 * 60) + (minutes * 60)
            machine_inst.timer_obj.reset_start_time()
            machine_inst.timer_obj.set_stop_time(total_secs)
            self.timer_manager.add_timerd_obj(machine_inst.timer_obj)
        else:
            machine_inst.timer_obj.reset_start_time()
            self.timer_manager.add_timerd_obj(machine_inst.timer_obj)
        
        if not price_per_hour:
            price_per_hour = self.get_price_per_hour(machine_inst)
        
        machine_inst.unblock(registred, limited, user_id, time, price_per_hour)
    
    def block(self, machine_inst, after, action):
        """
            Block a machine
            @machine_inst:
                MachineInst object representing a machine
            @after:
                True or False, if True a action will be realized after blocking
                machine, case True @action cannot be a None Value
            @action:
                Action will be realized after blocking machine
        """
        machine_inst.block(after, action)
    
    def get_price_per_hour(self, machine_inst):
        if machine_inst.category_id:
            c = self.machine_category_manager.get_all().filter_by(
                                        id=machine_inst.category_id).one()
            
            if c.custom_price_hour:
                price_per_hour = c.price_hour
            else:
                price_per_hour = self.conf_client.get_float(
                    'price_per_hour')
            
        else:
            price_per_hour = self.conf_client.get_float(
                    'price_per_hour') #TODO: Guardar preço na instancia e monitorar pelo monitory_add
        
        return price_per_hour
    
    def discount_credit(self, machine_inst, value):
        """
            Discount credit for registred mode
            @machine_inst:
                MachineInst object representing a machine
            @value:
                value to be discounted
        """
        cur_credit = self.users_manager.get_credit(
                            User.id, machine_inst.user_id)

        assert cur_credit >=0, "Credit cannot negative" 
        
        bloqued = False
        if (cur_credit - value) <= 0:
            bloqued = True

        cur_credit -= value
        
        if cur_credit < 0:
            print machine_inst, "Credit cannot be negative"
            cur_credit = 0.0

        if not(bloqued) and machine_inst.session:
            machine_inst.session.request('set_status', {'credit': cur_credit})
        
        self.users_manager.update_credit(machine_inst.user_id, cur_credit)
        
        if bloqued:
            machine_inst.block(False, 0)

    def update_total_to_pay(self, machine_inst, value):
        """
            Update total to pay for non registred mode
            @machine_inst:
                MachineInst object representing a machine
            @value:
                value to be updated
        """
        if machine_inst.session:
            machine_inst.session.request('set_status', {'total_to_pay': value})
        
        self.emit('update_total_to_pay', machine_inst, value)
    
    def machine_login(self, machine_inst, username, password):
        """
            Machine user login
            @machine_inst:
                MachineInst object representing a machine
            @username:
                User to be loged in
            @password:
                Password
        """
        if not self.server.information['login_suport']:
            return False
        
        if machine_inst.status != MACHINE_STATUS_AVAIL:
            return False
        
        o = self.server.users_manager.check_user(username, md5_cripto(password))
        
        if not o:
            return False
        
        user_id, credit= o
        
        if not credit:
            return 2
        
        
        users_manager = self.server.users_manager
        user = users_manager.get_all().filter_by(id=user_id).one()
        
        if user.category_id:
            if not user.category.allow_login:
                return 3
        
        user.login_count += 1
        user.last_login = datetime.datetime.now()
        user.last_machine_id = machine_inst.id
        users_manager.update(user)
        
        #Get Category price per hour
        if user.category_id:
            if user.category.custom_price_hour:
                price_per_hour = user.category.price_hour
            else:
                price_per_hour = self.get_price_per_hour(machine_inst)# get common hourly rate
        else:
            price_per_hour = self.get_price_per_hour(machine_inst)# get common hourly rate
        
        self.unblock(machine_inst, True, False, 
                     user_id, None, price_per_hour=price_per_hour)
        
        return True
    
    def machine_logout(self, machine_inst):
        """
            Machine user logout
            @machine_inst:
                MachineInst object representing a machine
        """
        machine_inst.block(False, 0)
        return True
    
    def add_time(self, machine_inst, a):
        """
            Add time for a machine
            @machine_inst:
                MachineInst object representing a machine
            @a:
                a tuple containing the time to be added (hours, minutes)
        """
        assert machine_inst.limited
        c = machine_inst.time
        t_time = (((c[0] * 3600) + (c[1] * 60)) + ((a[0] * 3600) + (a[1] * 60)))
        
        hour, minutes, seconds = humanize_time(t_time)
        machine_inst.time = (hour, minutes)
        machine_inst.timer_obj.set_stop_time(t_time)
        
        elapsed_time = int(time.time() - machine_inst.timer_obj._start_time)
        left_time = machine_inst.timer_obj._stop_time - elapsed_time
        
        data = {'time': machine_inst.time, 
                'left_time': left_time,
                'elapsed': elapsed_time
               }
        
        machine_inst.session.request('set_status', data)
    
    def remove_time(self, machine_inst, a):
        """
            Remove time for a machine
            @machine_inst:
                MachineInst object representing a machine
            @a:
                a tuple containing the time to be removed (hours, minutes)
        """
        
        assert machine_inst.limited
        c = machine_inst.time
        t_time = (((c[0] * 3600) + (c[1] * 60)) - ((a[0] * 3600) + (a[1] * 60)))
        
        elapsed_time = int(time.time() - machine_inst.timer_obj._start_time)
        
        if elapsed_time >= t_time:
            self.block(machine_inst, False, 0)
            return
        
        hour, minutes, seconds = humanize_time(t_time)
        machine_inst.time = (hour, minutes)
        machine_inst.timer_obj.set_stop_time(t_time)
        
        elapsed_time = int(time.time() - machine_inst.timer_obj._start_time)
        left_time = machine_inst.timer_obj._stop_time - elapsed_time
        
        data = {'time': machine_inst.time, 
                'left_time': left_time,
                'elapsed': elapsed_time
               }
        
        machine_inst.session.request('set_status', data)
        
class Server(gobject.GObject):
    
    common_background = None
    common_logo = None
    information = {}
    
    enabled_plugins = []
    
    def __init__(self):
        self.__gobject_init__()
        
        self.logger = logging.getLogger('server.daemon')
        
        self.conf_client = get_default_client()
        #
        
        #check psyco mode
        if self.conf_client.get_bool('use_psyco'):
            self.logger.info('Psyco Suport enabled')
            
            try:
                import psyco
            except:
                self.logger.warnig('Psyco not installed, please install it')
            else:
                self.logger.info('Starting up psyco')
                psyco.full()
        
        try:
            port = self.conf_client.get_int('listen_port')
            
            if not port:
                port = 4558
            
            self.netserver = NetServer(('', port), RequestHandler,
                                   SERVER_TLS_KEY, SERVER_TLS_CERT)
            
        except Exception, msg:
            try:
                err_ex = msg[1]
            except:
                err_ex = msg
            
            self.logger.critical("Cannot listen OpenLanHouse Server:%s" % err_ex)
            
            dialogs.ok_only("<big><b>%s</b></big>\n\n%s" % (
                            _("Cannot listen OpenLanHouse Server"), 
                            err_ex))
            
            import sys; sys.exit(3)
        
        string_keys = {
            'name': 'name',
            'admin_email': 'admin_email',
            'currency': 'currency'
        }
        
        bool_keys = {
            'login_suport': 'login_suport',
            'ticket_suport': 'ticket_suport',
            'default_welcome_msg': 'default_welcome_msg',
            'use_background': 'background',
            'use_logo': 'logo'
        }
        
        for name in string_keys.keys():
            value = self.conf_client.get_string(string_keys[name])
            
            if value: #FIXED BUG: XMLPICKLER cannot allow None
                self.information[name] = value
        
        for name in bool_keys.keys():
            value = self.conf_client.get_bool(bool_keys[name])
            self.information[name] = value
        
        self.information['price.hour'] = self.conf_client.get_float(
                                        'price_per_hour')
        
        if self.information['ticket_suport']:
            self.information['ticket_size'] = self.conf_client.get_int(
                                           'ticket_size')
        
        if not self.information['default_welcome_msg']:
            self.information['welcome_msg'] = self.conf_client.get_string(
                                           'welcome_msg')
        
        #Connect into database
        sql_data = {}
        sql_strings_values = {
            'engine': 'db/engine',
            'custom_sqlite_file': 'db/custom_sqlite_file',
            'host': 'db/host',
            'database': 'db/database',
            'user': 'db/user',
            'password': 'db/password'
        }
        
        for name in sql_strings_values.keys():
            sql_data[name] = self.conf_client.get_string(
                                    sql_strings_values[name])
        
        sql_data['port'] = self.conf_client.get_int(
                                    'db/port')
        
        sql_data['db_type'] = DB_NAMES.index(sql_data['engine'])
        
        if not sql_data['custom_sqlite_file']:
            sql_data['sqlite_file'] = SQLITE_FILE
        else:
            sql_data['sqlite_file'] = sql_data['custom_sqlite_file']
            
        try:
            self.db_session = DBSession(sql_data['db_type'],
                                        db_file = sql_data['sqlite_file'],
                                        host = sql_data['host'],
                                        user = sql_data['user'],
                                        password = sql_data['password'],
                                        database = sql_data['database'],
                                        port=sql_data['port'],
                                        echo = False,
                                        auto_commit = True)
        
        except Exception, error:
            print error
            dialogs.ok_only(_("<big><b>Cannot connect into database</b></big>") +
                             "\n\n%s" % error)
            import sys; sys.exit(4)
        
        #Tables managers
        self.version_manager = VersionManager(self.db_session)
        self.machine_manager = MachineManager(self.db_session)
        self.machine_category_manager = MachineCategoryManager(self.db_session)
        self.user_category_manager = UserCategoryManager(self.db_session)
        self.users_manager = UserManager(self.db_session)
        self.cash_flow_manager = CashFlowManager(self.db_session)
        self.open_debts_machine_manager = OpenDebtsMachineManager(
                                                             self.db_session)
        self.open_debts_other_manager = OpenDebtsOtherManager(
                                                             self.db_session)
        self.history_manager = HistoryManager(self.db_session)
        
        
        #Create Tables
        self.db_session.create_all()
        
        #Database Version!
        version = self.version_manager.get_all().filter_by(name="database_version").all()
        
        if not version:
            version = Version("database_version", APP_VERSION)
            self.version_manager.insert(version)
        else:
            version = version[0]
            if version.value == APP_VERSION:
                pass
            elif version.value < APP_VERSION:
                print "Downgrade database is not implemented yet"
            else:
                print "Upgrade database is not implemented yet"
        
        #Machine Inst manager
        self.instmachine_manager = InstManager(self,
                                               self.netserver,
                                               self.machine_manager,
                                               self.machine_category_manager,
                                               self.users_manager)
        
        #Timer Manager!
        self.timer_manager = self.instmachine_manager.timer_manager
        self.timer_manager.run()
        
        self.common_background = self.conf_client.get_string(
                                   'background_path')
                                   
        self.common_logo = self.conf_client.get_string(
                                   'logo_path')
        
        #generate background md5s
        if self.common_background and os.path.exists(self.common_background):
            try:
                self.information['background_md5'] = md5_cripto(open(
                                        self.common_background).read())
            except:
                pass
        
        if self.common_logo and os.path.exists(self.common_logo):
            try:
                self.information['logo_md5'] = md5_cripto(open(
                                        self.common_logo).read())
            except:
                pass
    
    def enable_plugin(self, plugin_name, main_window):
        """
            Enable a Plugin
            @plugin_name:
                a plugin name to be enabled
            @main_window:
                must be a OpenlhServer.ui.main.Manager object
        """
        
        #Set in configs
        plugins = self.conf_client.get_string_list('plugins')
        if not plugins:
            plugins = []
        
        if not plugin_name in plugins:
            plugins.append(plugin_name)
        self.conf_client.set_string_list('plugins', plugins)
        
        #Get the plugin module
        plugin = get_plugin(plugin_name)
        if not plugin:
            return
        
        if hasattr(plugin, "enable"):
            plugin.enable(self, main_window)
        
        if not plugin_name in self.enabled_plugins:
            self.enabled_plugins.append(plugin_name)
        
    def disable_plugin(self, plugin_name, main_window):
        """
            Disable a Plugin
            @plugin_name:
                a plugin name to be disabled
            @main_window:
                must be a OpenlhServer.ui.main.Manager object
        """
        
        #Set in configs
        plugins = self.conf_client.get_string_list('plugins')
        if not plugins:
            plugins = []
        
        if plugin_name in plugins:
            plugins.remove(plugin_name)
        self.conf_client.set_string_list('plugins', plugins)
        
        #Get the plugin module
        plugin = get_plugin(plugin_name)
        if not plugin:
            return
        
        #Call disable
        if hasattr(plugin, "disable"):
            plugin.disable(self, main_window)
        
        if plugin_name in self.enabled_plugins:
            self.enabled_plugins.remove(plugin_name)
    
    def plugin_is_enabled(self, plugin_name):
        """
            Check the plugin if is enabled
        """
        return plugin_name in self.enabled_plugins
    
    def load_plugins(self, main_window):
        """
            Load all plugins in settings
            @main_window:
                must be a OpenlhServer.ui.main.Manager object
        """
        
        plugins = self.conf_client.get_string_list('plugins')
        if not plugins:
            plugins = []
        
        for plugin_name in plugins:
            plugin = get_plugin(plugin_name)
            if not plugin:
                return
        
            if hasattr(plugin, "enable"):
                plugin.enable(self, main_window)
        
            if not plugin_name in self.enabled_plugins:
                self.enabled_plugins.append(plugin_name)
        
    @threaded
    def reload_configs(self):
        """
            Reload configs and send all alterations to all machines
        """
        
        self.logger.debug('reloading configurations')
        
        alterations = {}
        
        string_keys = {
            'name': 'name',
            'admin_email': 'admin_email',
            'currency': 'currency'
        }
        
        bool_keys = {
            'login_suport': 'login_suport',
            'ticket_suport': 'ticket_suport',
            'default_welcome_msg': 'default_welcome_msg',
            'use_background': 'background',
            'use_logo': 'logo'
        }
        
        for name in string_keys.keys():
            value = self.conf_client.get_string(string_keys[name])
            
            if (value != None and ((not(name in self.information)) or (name in self.information) and (self.information[name] != value))):
                self.information[name] = value
                alterations[name] = value
        
        for name in bool_keys.keys():
            value = self.conf_client.get_bool(bool_keys[name])
            
            if self.information[name] != value:
                self.information[name] = value
                alterations[name] = value
        
        value = self.conf_client.get_float('price_per_hour')
        if self.information['price.hour'] != value:
            self.information['price.hour'] = value
            alterations['price.hour'] = value
        
        if self.information['ticket_suport']:
            
            value = self.conf_client.get_int('ticket_size')
            
            if self.information.has_key('ticket_size'):
                if self.information['ticket_size'] != value:
                    self.information['ticket_size'] = value
                    alterations['ticket_size'] = value
            else:
                self.information['ticket_size'] = value
                alterations['ticket_size'] = value
        
        if not self.information['default_welcome_msg']:
            
            value = self.conf_client.get_string('welcome_msg')
            
            if self.information.has_key('welcome_msg'):
                if self.information['welcome_msg'] != value:
                    self.information['welcome_msg'] = value
                    alterations['welcome_msg'] = value
            else:
                self.information['welcome_msg'] = value
                alterations['welcome_msg'] = value
        
        value = self.conf_client.get_string('background_path')
        if self.common_background != value:
            self.common_background = value
            value2 = md5_cripto(open(self.common_background).read())
            self.information['background_md5'] = value2
            self.instmachine_manager.update_backgroud(value)
            
        value = self.conf_client.get_string('logo_path')
        if self.common_logo != value:
            self.common_logo = value
            value2 = md5_cripto(open(self.common_logo).read())
            self.information['logo_md5'] = value2
            self.instmachine_manager.update_logo(value)
        
        if alterations:
            self.instmachine_manager.update_information(alterations)
