# This file will be processed with automake to create Makefile.in

# ################ #
#  Automake Stuff  #
# ################ #

AUTOMAKE_OPTIONS = 1.9

AM_CFLAGS =				\
	$(WARN_CFLAGS)

MAINTAINERCLEANFILES =			\
	Makefile.in

EXTRA_DIST =				\
	applet.c			\
	applet.h		\
	load.c		\
	GNOME_OpenlhClientApplet.server.in.in \
	GNOME_OpenlhApplet.xml

# ################### #
#  The Applet Itself  #
# ################### #

libexec_PROGRAMS =					\
	openlh-client-applet

openlh_client_applet_CPPFLAGS =			\
	-DDATADIR=\""$(datadir)"\"			\
	$(APPLET_CFLAGS)				

openlh_client_applet_SOURCES =			\
	applet.c					\
	load.c

openlh_client_applet_LDADD =				\
	$(APPLET_LIBS)					

##############################
# Bonobo .server
##############################

serverdir =					\
	$(libdir)/bonobo/servers
server_in_files =				\
	GNOME_OpenlhClientApplet.server.in
server_DATA =					\
	$(server_in_files:.server.in=.server)

$(server_in_files): $(server_in_files:.server.in=.server.in.in)
	sed -e "s|\@LIBEXECDIR\@|$(libexecdir)|" -e "s|\@VERSION\@|$(VERSION)|" $< > $@

@INTLTOOL_SERVER_RULE@

##############################
# Bonobo UI
##############################

uidir =						\
	$(datadir)/gnome-2.0/ui

ui_DATA =					\
	GNOME_OpenlhApplet.xml

##############################
# Autojunk
##############################

CLEANFILES =					\
	$(server_in_files)			\
	$(server_DATA)				
