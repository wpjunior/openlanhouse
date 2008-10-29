iconsdir = $(datadir)/OpenlhClient/icons
icons_DATA = \
	openlh-client.png \
	openlh-client.svg 

scalabledir = $(datadir)/icons/hicolor/scalable/apps
scalable_DATA = openlh-client.svg

EXTRA_DIST = $(icons_DATA)

gtk_update_icon_cache = gtk-update-icon-cache -f -t $(datadir)/icons/hicolor

install-data-hook:
	@-if test -z "$(DESTDIR)"; then \
			echo "Updating Gtk icon cache."; \
			$(gtk_update_icon_cache); \
	else \
		    echo "*** Icon cache not updated.  After install, run this:"; \
		    echo "***   $(gtk_update_icon_cache)"; \
	fi
