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

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

GDM_PROTOCOL_PATH = "/var/run/gdm_socket"

from os import path as ospath
from os import environ as env
from os import name as osname
from OpenlhCore.utils import is_in_path, execute_command

try:
    from OpenlhClient import gdm
    HAS_GDM_CLIENT = True
except:
    HAS_GDM_CLIENT = False

class GdmActionManager:
    def __init__(self):
        pass
    
    def shutdown(self):
        if not gdm.supports_logout_action(gdm.LOGOUT_ACTION_SHUTDOWN):
            return False
        
        gdm.set_logout_action(gdm.LOGOUT_ACTION_SHUTDOWN)
        return self.logout()
        
    def reboot(self):
        if not gdm.supports_logout_action(gdm.LOGOUT_ACTION_REBOOT):
            return False
        
        gdm.set_logout_action(gdm.LOGOUT_ACTION_REBOOT)
        return self.logout()
        
    def logout(self):
        assert "GDMSESSION" in env, "Session must be specified by environ Variable GDMSESSION"
        session = env["GDMSESSION"]
        
        # Openbox
        if "openbox" in session.lower():
            p = is_in_path("openbox")
            
            if not p:
                return False
            
            cmd = [p, "--exit"]
            execute_command(cmd)
            
        # Send logout signal to GNOME
        elif "gnome" in session.lower():
            p = is_in_path("gnome-session-save")
            
            if not p:
                return False
            
            cmd = [p, "--logout"]
            a = execute_command(cmd)
        
        #TODO: write for kde, xfce4, fluxbox, blackbox and LXDE
        return True

class PosixActionManager:
    """
    Posix Action Manager
    """
    def __init__(self):
        pass
    
    def shutdown(self):
        executable = is_in_path("shutdown")
        if not executable:
            return False
        
        cmd = [executable, "-h", "now"]
        a = execute_command(cmd)
        print a
    
    def reboot(self):
        executable = is_in_path("reboot")
        if not executable:
            return False
        
        a = execute_command(executable)
        print a
    
    def logout(self):
        #TODO: find session and send logout signal
        pass
    

class Win32ActionManager:
    """
    Win32 Action Manager
    """
    def __init__(self):
        pass
    
    def shutdown(self):
        cmd = ["shutdown", "-s", "-t", "0"]
        a = execute_command(cmd)
        print a
    
    def reboot(self):
        cmd = ["shutdown", "-r", "-t", "0"]
        a = execute_command(cmd)
        print a
    
    def logout(self):
        cmd = [executable, "-l"]
        a = execute_command(cmd)
        print a


if osname == "nt":              # if is running Windows NT
    ActionManager = Win32ActionManager()

elif (HAS_GDM_CLIENT 
    and (ospath.exists(GDM_PROTOCOL_PATH))
    and ("GDMSESSION" in env)):
    
    ActionManager = GdmActionManager()
    
elif osname == "posix":
    ActionManager = PosixActionManager()
