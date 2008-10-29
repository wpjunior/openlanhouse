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

AC_INIT([OpenLanhouse Core],[0.2],[http://trac.openlanhouse.org],[openlh-core])
AC_PROG_LIBTOOL
AC_PROG_CC
AM_INIT_AUTOMAKE([1.7])
AM_MAINTAINER_MODE

dnl python checks
AM_PATH_PYTHON(2.5)

PY_PREFIX=`$PYTHON -c 'import sys ; print sys.prefix'`
PYTHON_LIBS="-lpython$PYTHON_VERSION"
PYTHON_CFLAGS="-I$PY_PREFIX/include/python$PYTHON_VERSION"

AC_SUBST([PYTHON_LIBS])
AC_SUBST([PYTHON_CFLAGS])

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

#GnuTLS
dnl Checking GnuTLS Libraries
PKG_CHECK_MODULES(GNUTLS,
    gnutls >= 2.4.0
)

AC_SUBST(GNUTLS_CFLAGS)
AC_SUBST(GNUTLS_LIBS)

dnl output files
AC_CONFIG_FILES([
Makefile
src/Makefile
src/certtool/Makefile
src/OpenlhCore/Makefile
src/OpenlhCore/net/Makefile
src/OpenlhCore/net/backends/Makefile
src/OpenlhCore/net/certgen/Makefile
src/OpenlhCore/config.py
])

AC_OUTPUT

echo "
openlh-core-$VERSION:

	prefix:                 ${prefix}

"
