#!/usr/bin/env python
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

import os
import shutil
import ctypes
import traceback
import threading
import subprocess
from hashlib import md5

WIN_VERSION = {
    (1, 4, 0): '95',
    (1, 4, 10): '98',
    (1, 4, 90): 'ME',
    (2, 4, 0): 'NT',
    (2, 5, 0): '2000',
    (2, 5, 1): 'XP',
    (2, 5, 2): '2003',
    (2, 6, 0): 'Vista',
}

DISTRO_INFO = {
    'Arch Linux': '/etc/arch-release',
    'Aurox Linux': '/etc/aurox-release',
    'Big Linux': '/etc/atualizacao/bigversao',
    'Conectiva Linux': '/etc/conectiva-release',
    'CRUX': '/usr/bin/crux',
    'Debian GNU/Linux': '/etc/debian_release',
    'Debian GNU/Linux': '/etc/debian_version',
    'Fedora Linux': '/etc/fedora-release',
    'Gentoo Linux': '/etc/gentoo-release',
    'Linux from Scratch': '/etc/lfs-release',
    'Mandrake Linux': '/etc/mandrake-release',
    'Slackware Linux': '/etc/slackware-release',
    'Slackware Linux': '/etc/slackware-version',
    'Solaris/Sparc': '/etc/release',
    'Source Mage': '/etc/sourcemage_version',
    'SUSE Linux': '/etc/SuSE-release',
    'Sun JDS': '/etc/sun-release',
    'PLD Linux': '/etc/pld-release',
    'Yellow Dog Linux': '/etc/yellowdog-release',
    'Redhat Linux': '/etc/redhat-release'
}

def rename_process(name):
    """rename process by libc"""
    if os.name == 'posix':
        try:
            libc = ctypes.CDLL('/lib/libc.so.6')
            libc.prctl(15, name, 0, 0, 0)
        except:
            pass

def remove_path(path):
    """ Removes a directory path """
    try:
        shutil.rmtree(path, ignore_errors=False)
    except Exception , e:
        print str(e)
        pass


def mkdir(path, remove_existing=False):
    """ 
        Create a full path, directory by directory
        if removeExisting is set it will remove main folder and contents before creation.
    """

    #remove directiory if already exists
    if remove_existing:
        if os.path.exists(path):
            remove_path(path)

    if not os.path.exists(path):
        os.makedirs(path)

    return path

def md5_cripto(text):
    """Criptografy Text into MD5"""
    return md5(text).hexdigest()


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
            return False

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
                        text = get_output_of_command(path_to_file).splitlines()[0]
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

