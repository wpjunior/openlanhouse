SUBDIRS = ui glade icons 

uidir = $(datadir)/OpenlhClient

desktopdir = $(datadir)/applications
desktop_in_files = openlh-client.desktop.in openlh-client-config.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

schemadir = $(GCONF_SCHEMA_FILE_DIR)
schema_in_files = openlh-client.schemas.in
schema_DATA = openlh-client.schemas
@INTLTOOL_SCHEMAS_RULE@

CLEANFILES = \
	openlh-client.schemas \
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
