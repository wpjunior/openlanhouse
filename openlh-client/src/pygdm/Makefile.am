openlhdir = $(pythondir)/OpenlhClient
openlh_LTLIBRARIES = gdm.la

gdm_la_LDFLAGS = \
	-module \
	-avoid-version

gdm_la_CPPFLAGS = \
	$(PYTHON_CFLAGS) \
	$(PYGDM_CFLAGS)

gdm_la_LIBADD = \
	$(PYTHON_LIBS) \
	$(PYGDM_LIBS)

gdm_la_SOURCES = \
	gdm-logout-action.c \
   	gdm-logout-action.h \
   	main.c
