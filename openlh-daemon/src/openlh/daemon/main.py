#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2011 Wilson Pinto Júnior <wilsonpjunior@gmail.com>
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

from gi.repository import GObject
from openlh.core.config_client import get_default_client
from openlh.core.os_utils import threaded

class Daemon:
    def __init__(self):

        self.conf_client = get_default_client()
        
        self.name = self.conf_client.get_string("name")

        self.admin_email = self.conf_client.get_string(
                                          "admin_email")
        
        self.price_per_hour = self.conf_client.get_float(
                                          "price_per_hour")
        
        #setup price per hour
        #if not self.price_per_hour:
        #    dlg = dialogs.set_price_per_hour()
        #    self.price_per_hour = dlg.run()
        #    if self.price_per_hour == None:
        #        sys.exit(0)
        #    
        #    self.conf_client.set_float("price_per_hour", 
        #                                self.price_per_hour)
    
    @threaded
    def send_registration(self):
        """
        send you lan house status for openlanhouse.org
        """
        
        if not CONFIG_PATH_EXISTS: #skip first execution
            return
        
        if os.path.exists(I_AM_DEVELOPER_FILE): #skip developers :)
            return
        
        reg_file = os.path.join(REGISTRATION_DIR, APP_VERSION)
        if os.path.exists(reg_file):
            return
        
        import httplib
        import urllib
        data = {'lan_name': self.name,
                'admin_email': self.admin_email,
                'app_version': APP_VERSION,
                }
        
        t = get_os()
        if t[0]:
            data['os_name'] = t[0]
        else:
            data['os_name'] = ""
            
        if t[1]:
            data['os_version'] = t[1]
        else:
            data['os_version'] = ""

        params = urllib.urlencode(data)

        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        
        try:
            print "Sending you status for openlanhouse.org"
            conn = httplib.HTTPConnection("openlanhouse.org")
            conn.request("POST", "/status/send", params, headers)
            response = conn.getresponse()
        except:
            print "Failed to connect in openlanhouse.org"
            return
        
        if response.status == 200:
            open(reg_file, "wb").write(response.read())
        else:
            open(reg_file, "wb").write("")
        

    def run(self):
    
        #self.send_registration() #Send Status to openlanhouse.org

        try:
            GObject.MainLoop().run()
        except KeyboardInterrupt:
            pass
