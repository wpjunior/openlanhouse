#  Copyright (C) 2008 Wilson Pinto Júnior (N3RD3X) <n3rd3x@guake-terminal.org>
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

AC_INIT([OpenLanhouse Client],[0.1],[http://openlanhouse.sf.net],[openlh-client])
AM_CONFIG_HEADER(config.h)
AM_INIT_AUTOMAKE([1.7])
AM_MAINTAINER_MODE
AC_PROG_CC

AC_DEFUN([AC_DEFINE_PATH], [
    test "x$prefix" = xNONE && prefix="$ac_default_prefix"
    test "x$exec_prefix" = xNONE && exec_prefix='${prefix}'
    ac_define_path=`eval echo [$]$2`
    ac_define_path=`eval echo [$]ac_define_path`
    $1="$ac_define_path"
    AC_SUBST($1)
    ifelse($3, ,
        AC_DEFINE_UNQUOTED($1, "$ac_define_path"),
        AC_DEFINE_UNQUOTED($1, "$ac_define_path", $3))
    ])

GETTEXT_PACKAGE=openlh-client
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE],["$GETTEXT_PACKAGE"],[Gettext package])
AC_DEFINE_PATH(GNOMELOCALEDIR, "${datadir}/locale", [locale directory])
AC_DEFINE_PATH(DATADIR, "${datadir}", [datadir directory])
AC_PROG_INTLTOOL([0.35.0])
AM_GLIB_GNU_GETTEXT
AM_GCONF_SOURCE_2
AM_PROG_LIBTOOL

AC_PATH_PROG(GCONFTOOL, gconftool-2, no)

dnl python checks
AM_PATH_PYTHON(2.5)

dnl gtk dependencie
PYGTK_REQUIRED=2.12.0
PANEL_REQUIRED_VERSION=2.0.0

PKG_CHECK_MODULES([DEPENDENCIES], [
    pygtk-2.0 >= $PYGTK_REQUIRED
])


PKG_CHECK_MODULES(APPLET,
    gtk+-2.0 >= 2.12.0
    libpanelapplet-2.0 >= $PANEL_REQUIRED_VERSION
    dbus-glib-1
)

AC_SUBST(APPLET_CFLAGS)
AC_SUBST(APPLET_LIBS)

#python-gnutls
dnl Checking python-gnutls
AC_MSG_CHECKING([for the python-gnutls package])
ac_pgnutls_result=`$PYTHON -c 'try:
    import gnutls
    import gnutls.crypto
    import gnutls.connection
except Exception, e:
    print str(e)' 2> /dev/null`

if test -z "$ac_pgnutls_result"; then
    AC_MSG_RESULT([yes])
else
    AC_MSG_RESULT([no])
    AC_MSG_ERROR([cannot import Python module "gnutls".
    Please check if you have python-gnutls installed. The error was:
    $ac_pgnutls_result])
fi

#python-gconf
dnl Checking python-gconf
AC_MSG_CHECKING([for the python-gconf package])
ac_pgconf_result=`$PYTHON -c 'try:
    import gconf
except Exception, e:
    print str(e)' 2> /dev/null`

if test -z "$ac_pgconf_result"; then
    AC_MSG_RESULT([yes])
else
    AC_MSG_RESULT([no])
    AC_MSG_ERROR([cannot import Python module "gconf".
    Please check if you have python-gconf installed. The error was:
    $ac_pgconf_result])
fi

#python-certtool
dnl Checking python-certtool
AC_MSG_CHECKING([for the python-certtool package])
ac_pgconf_result=`$PYTHON -c 'try:
    import certtool
except Exception, e:
    print str(e)' 2> /dev/null`

if test -z "$ac_pgconf_result"; then
    AC_MSG_RESULT([yes])
else
    AC_MSG_RESULT([no])
    AC_MSG_ERROR([cannot import Python module "certtool".
    Please check if you have python-certtool installed. The error was:
    $ac_pgconf_result])
fi


dnl output files
AC_CONFIG_FILES([
Makefile
data/Makefile
data/openlh-client.desktop.in
data/glade/Makefile
data/ui/Makefile
data/icons/Makefile
gnomeapplet/Makefile
src/Makefile
src/OpenlhClient/Makefile
src/OpenlhClient/ui/Makefile
src/OpenlhClient/config.py
po/Makefile.in
])

AC_OUTPUT

echo "
openlh-client-$VERSION:

	prefix:                 ${prefix}

"
