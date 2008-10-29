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
from hashlib import md5
import threading
import time
import traceback
import logging
import socket
import subprocess
import errno
from gtk import gdk
from gtk import Builder

HAS_PYWIN32 = False

if os.name == 'nt':
    HAS_PYWIN32 = True
    
    try:
        import winsound # windows-only built-in module for playing wav
        import win32api
        import win32file
        import win32con
        import pywintypes
    
    except ImportError:
        HAS_PYWIN32 = False

def rename_process(name):
    """rename process by libc"""
    if os.name == 'posix':
        try:
            libc = dl.open('/lib/libc.so.6')
            libc.call('prctl', 15, '%s\0' % name, 0, 0, 0)
        except:
            pass

def is_in_path(name_of_command, return_abs_path=True):
    # if return_abs_path is True absolute path will be returned
    # for name_of_command
    # on failures False is returned
    
    is_in_dir = False
    found_in_which_dir = None
    path = os.getenv('PATH').split(':')
    
    for path_to_directory in path:
        try:
            contents = os.listdir(path_to_directory)
        
        except OSError: # user can have something in PATH that is not a dir
            pass
        
        else:
            is_in_dir = name_of_command in contents
        
        if is_in_dir:
            if return_abs_path:
                found_in_which_dir = path_to_directory
            
            break

    if found_in_which_dir:
        abs_path = os.path.join(path_to_directory, name_of_command)
        return abs_path
    
    else:
        return is_in_dir

def execute_command(cmd):
    """
        Execute command
    """
    if not isinstance(cmd, list):
        cmd = [cmd]
        
    env = os.environ
    po = subprocess.Popen(cmd, stdin=None, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, env=env)
    
    retval = po.wait()
    (stdout, stderr) = po.communicate()
    
    return (stdout, stderr, retval)

def removePath(path):
    """ Removes a directory path """
    try:
        shutil.rmtree(path, ignore_errors=False)
    except Exception , e:
        print str(e)
        pass

def mkdir(path, RemoveExisting=False):
    """ 
        Create a full path, directory by directory
        if removeExisting is set it will remove main folder and contents before creation.
    """

    #remove directiory if already exists
    if RemoveExisting:
        if os.path.exists(path):
            removePath(path)

    if not os.path.exists(path):
        os.makedirs(path)

    return path

class DictLimited:
    def __init__(self, limit):
        self._dict = dict()
        self._limit = limit
    
    def __setitem__(self, key, value):
        if not key in self._dict:
            assert len(self._dict) +1 <= self._limit, "this dict is full"
        self._dict[key] = value
    
    def __getitem__(self, key):
        return self._dict[key]
    
    def __delitem__(self, key):
        self._dict.pop(key)
    
    def __str__(self):
        return "<DictLimited(%s)>" % self._dict.__repr__()
    
    def __getattr__(self, attr_name):
        return getattr(self._dict, attr_name)

def compress(source, dest = ''):
    """
        Compress a file using bz2 compression.
    """
    if dest == '':
        dest = source

    dest_ext = '.bz2'
    arcname = os.path.basename (source)
    dest_name = '%s%s' % (dest, dest_ext)
    dest_path = os.path.join(dest, dest_name)

    try:
        input = bz2.compress(file(source, 'r').read())
        out = file(dest_path,'w')
        out.write(input)
        out.close()
    except Exception , e:
        return False, str(e)

    return True, dest_path

def zip_file(source, dest):
    try:
        fileObj = gzip.GzipFile(os.path.join(source), 'wb');
        fileObj.write(file(os.path.join(dest), 'rb').read())
        fileObj.close()
        return True, ''
    except Exception, e:
        return False, str(e)

def humanize_file_size( i):
    """
        Taken from jinja
        Format the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
        102 bytes, etc).
    """
    try:
        bytes = float(i)
    except:
        bytes = 0

    if bytes < 1024:
        return u"%d Byte%s" % (bytes, bytes != 1 and u's' or u'')
    elif bytes < 1024 * 1024:
        return u"%.1f KB" % (bytes / 1024)
    elif bytes < 1024 * 1024 * 1024:
        return u"%.1f MB" % (bytes / (1024 * 1024))
    else:
        return u"%.1f GB" % (bytes / (1024 * 1024 * 1024))

## Check order
## 0 = OK
## 1 = Fault
## 2 = Warning
## 3 = Error

def check_nick(text):
    """Check Nick Entry is Valid"""
    if "" == text: #TODO ADD PARADAS de checagem de caracteres proibidos
        return 1
    elif " " in text:
        return 3
    elif MIN_NICK <= len(text):
        return 0
    else:
        return 2

def check_email(text):
    """Check Email Entry is Valid"""
    email_regex = re.compile(r'\w+[@]\w+[.]\w{2,}.*')
    
    if "" == text:
        return 1
    elif email_regex.search(text):
        return 0
    else:
        return 2
    
def check_name(text):
    """Check Name Entry is Valid"""
    if bool(text):
        return 0
    else:
        return 1

def md5_cripto(text):
    """Criptografy Text into MD5"""
    return md5(text).hexdigest()

def threaded(f):
    """
        Threads Wrapper
    """
    def wrapper(*args):
        t = threading.Thread(target=f, args=args)
        t.setDaemon(True)
        t.start()
    wrapper.__name__ = f.__name__
    wrapper.__dict__ = f.__dict__
    wrapper.__doc__ = f.__doc__
    return wrapper

def get_windows_reg_env(varname, default=''):
    """
        asks for paths commonly used but not exposed as ENVs
        in english Windows 2003 those are:
        'AppData' = %USERPROFILE%\Application Data (also an ENV)
        'Desktop' = %USERPROFILE%\Desktop
        'Favorites' = %USERPROFILE%\Favorites
        'NetHood' = %USERPROFILE%\NetHood
        'Personal' = D:\My Documents (PATH TO MY DOCUMENTS)
        'PrintHood' = %USERPROFILE%\PrintHood
        'Programs' = %USERPROFILE%\Start Menu\Programs
        'Recent' = %USERPROFILE%\Recent
        'SendTo' = %USERPROFILE%\SendTo
        'Start Menu' = %USERPROFILE%\Start Menu
        'Startup' = %USERPROFILE%\Start Menu\Programs\Startup
        'Templates' = %USERPROFILE%\Templates
        'My Pictures' = D:\My Documents\My Pictures
        'Local Settings' = %USERPROFILE%\Local Settings
        'Local AppData' = %USERPROFILE%\Local Settings\Application Data
        'Cache' = %USERPROFILE%\Local Settings\Temporary Internet Files
        'Cookies' = %USERPROFILE%\Cookies
        'History' = %USERPROFILE%\Local Settings\History
    """

    if os.name != 'nt':
        return ''

    val = default
    try:
        rkey = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,
        r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders')
        try:
            val = str(win32api.RegQueryValueEx(rkey, varname)[0])
            val = win32api.ExpandEnvironmentStrings(val) # expand using environ
        except:
            pass
    
    finally:
        win32api.RegCloseKey(rkey)
    
    return val

def get_my_pictures_path():
    """
        Windows-only atm. [Unix lives in the past]
    """
    return get_windows_reg_env('My Pictures')

def get_desktop_path():
    if os.name == 'nt':
        path = get_windows_reg_env('Desktop')
    else:
        path = os.path.join(os.path.expanduser('~'), 'Desktop')
    
    return path

def get_documents_path():
    if os.name == 'nt':
        path = get_windows_reg_env('Personal')
    
    else:
        path = os.path.expanduser('~')
    
    return path

def execute_command(cmd):
    """
        Execute command
    """
    if not isinstance(cmd, list):
        cmd = [cmd]
        
    env = os.environ
    po = subprocess.Popen(cmd, stdin=None, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, env=env)
    
    retval = po.wait()
    (stdout, stderr) = po.communicate()
    
    return (stdout, stderr, retval)


def get_output_of_command(command):
    try:
        child_stdin, child_stdout = os.popen2(command)
    except ValueError:
        return None

    output = child_stdout.readlines()
    child_stdout.close()
    child_stdin.close()

    return output

def decode_filechooser_file_paths(file_paths):
    """
        decode as UTF-8 under Windows and
        ask sys.getfilesystemencoding() in POSIX
        file_paths MUST be LIST
    """
    file_paths_list = list()
    
    if os.name == 'nt': # decode as UTF-8 under Windows
        for file_path in file_paths:
            file_path = file_path.decode('utf8')
            file_paths_list.append(file_path)
    
    else:
        for file_path in file_paths:
            try:
                file_path = file_path.decode(sys.getfilesystemencoding())
            except:
                try:
                    file_path = file_path.decode('utf-8')
                except:
                    pass
            file_paths_list.append(file_path)
    
    return file_paths_list


def get_os():
    """
        Return os_name and os_version
    """
    
    def convert(x):
        x = x.strip().replace('n/a', '').replace('N/A', '')
        if x:
            return x
    
    name = None
    version = None
    
    if os.name == 'posix':
        executable = 'lsb_release'
        full_path_to_executable = is_in_path(executable, return_abs_path=True)
        
        if full_path_to_executable:
            (tmp1, a, b) = execute_command([executable, '-i', '--short'])
            (tmp2, a, b) = execute_command([executable, '-c', '--short'])
            (tmp3, a, b) = execute_command([executable, '-r', '--short'])
            
            if convert(tmp1):
                name = convert(tmp1)
            
            if convert(tmp2):
                version = convert(tmp2)
                
            if convert(tmp3) and version:
                version = version + ' (' + convert(tmp3) + ')'
        
        if not name:
            for distro_name in DISTRO_INFO:
                path_to_file = DISTRO_INFO[distro_name]
                
                if os.path.exists(path_to_file):
                    if os.access(path_to_file, os.X_OK):
                        # the file is executable (f.e. CRUX)
                        # yes, then run it and get the first line of output.
                        text = get_output_of_command(path_to_file)[0]
                    else:
                        fd = open(path_to_file)
                        text = fd.readline().strip() # get only first line
                        fd.close()
                        if path_to_file.endswith('version'):
                            # sourcemage_version and slackware-version files
                            # have all the info we need (name and version of distro)
                            if not os.path.basename(path_to_file).startswith(
                            'sourcemage') or not\
                            os.path.basename(path_to_file).startswith('slackware'):
                                name = distro_name
                                version = text
                        
                        elif path_to_file.endswith('aurox-release'):
                            #    file doesn't have version
                            name = distro_name
                            
                        elif path_to_file.endswith('lfs-release'): # file just has version
                            name = distro_name
                            version = text
                    
                    break
        
        if not name:
            tmp = os.uname()
            name = tmp[0]
            version = tmp[2]
    
    elif os.name == 'nt':
        ver = os.sys.getwindowsversion()
        ver_format = ver[3], ver[0], ver[1]
        
        name = 'Windows'
        
        if WIN_VERSION.has_key(ver_format):
            version = WIN_VERSION[ver_format]
            
    elif os.name == 'ce':
        name = 'Windows'
        version = 'CE'
    
    elif os.name == 'mac':
        name = 'MacOS'
    
    return (name, version)

def calculate_time(price_per_hour, credit):
    """
        Calculate Time per credit
        returns a tuple contain (hours, minutes, seconds)
    """
    t = float(credit) / float(price_per_hour)
    
    hour = int(t)
    rest = float(t) % float(1)
    r = rest * 60
    
    minute = int(r)
    seconds = int((r - int(r)) * 60)
    del t, r
    return (hour, minute, seconds)

def calculate_credit(price, hour, minute, seconds):
    """
        Calculate Credit per hour
        returns a float contain credit
    """
    return ((hour+(float(minute)/60)+((float(seconds)/60)/100)) * price)

def humanize_time(mtime):
    secs = mtime % 60
    minutes = (mtime // 60) % 60
    hour = (mtime // (60 * 60)) % 60
    return hour, minutes, secs

def pid_alive(app, path):
    try:
        pf = open(path)
    
    except:
        # probably file not found
        return False

    try:
        pid = int(pf.read().strip())
        pf.close()
    except:
        traceback.print_exc()
        # PID file exists, but something happened trying to read PID
        # Could be 0.10 style empty PID file, so assume app is running
        return True

    if os.name == 'nt':
        try:
            from ctypes import windll, c_ulong, c_int
            from ctypes import Structure, c_char, POINTER, pointer
        except:
            return True

        class PROCESSENTRY32(Structure):
            _fields_ = [
                ('dwSize', c_ulong, ),
                ('cntUsage', c_ulong, ),
                ('th32ProcessID', c_ulong, ),
                ('th32DefaultHeapID', c_ulong, ),
                ('th32ModuleID', c_ulong, ),
                ('cntThreads', c_ulong, ),
                ('th32ParentProcessID', c_ulong, ),
                ('pcPriClassBase', c_ulong, ),
                ('dwFlags', c_ulong, ),
                ('szExeFile', c_char*512, ),
                ]
            def __init__(self):
                Structure.__init__(self, 512+9*4)

        k = windll.kernel32
        k.CreateToolhelp32Snapshot.argtypes = c_ulong, c_ulong,
        k.CreateToolhelp32Snapshot.restype = c_int
        k.Process32First.argtypes = c_int, POINTER(PROCESSENTRY32),
        k.Process32First.restype = c_int
        k.Process32Next.argtypes = c_int, POINTER(PROCESSENTRY32),
        k.Process32Next.restype = c_int

        def get_p(p):
            h = k.CreateToolhelp32Snapshot(2, 0) # TH32CS_SNAPPROCESS
            assert h > 0, 'CreateToolhelp32Snapshot failed'
            b = pointer(PROCESSENTRY32())
            f = k.Process32First(h, b)
            while f:
                if b.contents.th32ProcessID == p:
                    return b.contents.szExeFile
                f = k.Process32Next(h, b)

        if get_p(pid) in ('python.exe', '%s.exe' % app):
            return True
        return False
    try:
        if not os.path.exists('/proc'):
            return True # no /proc, assume running

        try:
            f = open('/proc/%d/cmdline'% pid) 
        except IOError, e:
            if e.errno == errno.ENOENT:
                return False # file/pid does not exist
            raise 

        n = f.read().lower()
        f.close()
        if n.find(app) < 0:
            return False
        return True # Running app found at pid
    except:
        traceback.print_exc()

    # If we are here, pidfile exists, but some unexpected error occured.
    # Assume running.
    return True