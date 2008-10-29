SUBDIRS = ui glade icons 

uidir = $(datadir)/OpenlhServer

desktopdir = $(datadir)/applications
desktop_in_files = openlh-server.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

schemadir = $(GCONF_SCHEMA_FILE_DIR)
schema_in_files = openlh-server.schemas.in
schema_DATA = openlh-server.schemas
@INTLTOOL_SCHEMAS_RULE@

CLEANFILES = \
	openlh-server.schemas \
	$(desktop_DATA)

EXTRA_DIST = \
	$(schema_in_files) \
	$(desktop_in_files) \
	$(desktop_DATA)

if GCONF_SCHEMAS_INSTALL
install-data-local:
	if test -z "$(DESTDIR)" ; then \
		for p in $(schema_DATA) ; do \
			GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) $(GCONFTOOL) --makefile-install-rule $$p; \
		done \
	fi
endif
