#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  
# Copyright (C) 2003-2006 Yann Le Boulanger <asterix@lagaule.org>
# Copyright (C) 2005-2006 Nikos Kouremenos <kourem@gmail.com>
#  Copyright (c) 2007-2008 Wilson Pinto Júnior (N3RD3X) <n3rd3x@guake-terminal.org>

# Copyright (C) 2005
#      Dimitur Kirov <dkirov@gmail.com>
#      Travis Shirk <travis@pobox.com>
#
#  APTonCD - Copyright (c) 2006.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import re
import shutil
import stat
import bz2
import gzip

try:
    import dl
except:
    dl = None

import base64
from md5 import md5
import threading
import time
import traceback
import logging
import socket
import subprocess
import errno
from gtk import gdk

from OpenlhClient.globals import *

def generate_id_bytime():
    from sha import sha
    
    cur_time = time.time()
    hash = sha(str(cur_time))
    
    return hash.hexdigest()