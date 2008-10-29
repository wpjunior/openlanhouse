openlhdir = $(pythondir)/OpenlhCore
openlh_LTLIBRARIES = certtool.la

certtool_la_LDFLAGS = \
	-module \
	-avoid-version

certtool_la_CPPFLAGS = \
	$(GNUTLS_CFLAGS) \
	$(PYTHON_CFLAGS)

certtool_la_LIBADD = \
	$(PYTHON_LIBS) \
	$(GNUTLS_LIBS)

certtool_la_SOURCES = \
	certtool.c \
	privkey.c \
	privkey.h \
	self-signed.c \
	self-signed.h \
	template.c \
	template.h
