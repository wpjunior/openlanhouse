#  Copyright (C) 2008-2009 Wilson Pinto Júnior <wilson@openlanhouse.org>
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

AC_INIT([OpenLanhouse Server],[0.2],[http://openlanhouse.org],[openlh-server])
AM_INIT_AUTOMAKE([1.7])
AM_MAINTAINER_MODE
GETTEXT_PACKAGE=openlh-server
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE],["$GETTEXT_PACKAGE"],[Gettext package])
AC_PROG_INTLTOOL([0.35.0])
AM_GLIB_GNU_GETTEXT

AM_GCONF_SOURCE_2
AM_PROG_LIBTOOL

AC_PATH_PROG(GCONFTOOL, gconftool-2, no)

if test x"$GCONFTOOL" = xno; then
  AC_MSG_ERROR([gconftool-2 executable not found in your path - should be installed with GConf])
  fi

dnl python checks
AM_PATH_PYTHON(2.5)

dnl gtk dependencie
PYGTK_REQUIRED=2.12.0
PKG_CHECK_MODULES([DEPENDENCIES], [
    pygtk-2.0 >= $PYGTK_REQUIRED
])

#python-sqlalchemy
dnl Checking python-sqlalchemy
AC_MSG_CHECKING([for the python-sqlalchemy package])
ac_psqlalchemy_result=`$PYTHON -c 'try:
    import sys
    import sqlalchemy
    from sqlalchemy import __version__
    if not __version__ >= "0.4":
        print "python-sqlalchemy must be 0.4 version or later"
        sys.exit(2)
except:
    print str(e)' 2> /dev/null`
exit_code=$?

if (("$exit_code"==0)); then
    AC_MSG_RESULT([yes])
else
    AC_MSG_RESULT([no])
    AC_MSG_ERROR([cannot import Python module "sqlalchemy".
    Please check if you have python-sqlalchemy installed. The error was:
    $ac_psqlalchemy_result])
fi

dnl output files
AC_CONFIG_FILES([
Makefile
data/Makefile
data/openlh-server.desktop.in
data/glade/Makefile
data/ui/Makefile
data/icons/Makefile
data/icons/status/Makefile
src/Makefile
src/OpenlhServer/Makefile
src/OpenlhServer/ui/Makefile
src/OpenlhServer/db/Makefile
src/OpenlhServer/http/Makefile
src/OpenlhServer/config.py
plugins/Makefile
plugins/example/Makefile
po/Makefile.in
])

AC_OUTPUT

echo "
openlh-server-$VERSION:

	prefix:                 ${prefix}

"
