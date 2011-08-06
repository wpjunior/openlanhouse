#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008 Wilson Pinto Júnior <wilsonpjunior@gmail.com>
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

from OpenlhCore import certtool

class PrivateKey:
    """
        Private Key Object
    """
    def __init__(self, privkey_obj):
        self.privkey_obj = privkey_obj
    
    def export(self):
        """
            Export private key in PEM format
        """
        return self.privkey_obj.export()

class Template(certtool.Template):
    """
        Template Object
    """
    def __init__(self, path):
        certtool.Template.__init__(self)

class SelfSigned:
    """
        SelfSigned Certificate
    """
    def __init__(self, selfsigned_obj):
        self.selfsigned_obj = selfsigned_obj
    
    def export(self):
        """
            Export self-signed Certificate in PEM format
        """
        return self.selfsigned_obj.export()

def generate_private_key(bits=1024):
    privkey_obj = certtool.generate_private_key(bits=bits)
    return PrivateKey(privkey_obj)

def generate_self_signed(privkey, template):
    certificate = certtool.generate_self_signed(privkey=privkey.privkey_obj,
                                                template=template,
                                                dig=certtool.DIG_SHA1)
    
    return SelfSigned(certificate)