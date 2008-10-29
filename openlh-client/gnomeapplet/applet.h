/**
 * Copyright (C) 2008 Wilson Pinto Júnior <wilson@openlanhouse.org>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef _APPLET_H
#define _APPLET_H
#include <glib.h>
#include <glib-object.h>
#include <gtk/gtk.h>
#include <panel-applet.h>
#include <dbus/dbus-glib.h>

G_BEGIN_DECLS
#define OPENLH_APPLET_TYPE                  (openlh_applet_get_type ())
#define OPENLH_APPLET(obj)                  (G_TYPE_CHECK_INSTANCE_CAST ((obj), OPENLH_APPLET_TYPE, OpenlhApplet))
#define OPENLH_APPLET_CLASS(klass)          (G_TYPE_CHECK_CLASS_CAST ((klass), OPENLH_APPLET_TYPE, OpenlhAppletClass))
#define IS_OPENLH_APPLET(obj)               (G_TYPE_CHECK_INSTANCE_TYPE ((obj), OPENLH_APPLET_TYPE))
#define IS_OPENLH_APPLET_CLASS(klass)       (G_TYPE_CHECK_CLASS_TYPE ((klass), OPENLH_APPLET_TYPE))
#define OPENLH_APPLET_GET_CLASS(obj)        (G_TYPE_INSTANCE_GET_CLASS ((obj), OPENLH_APPLET_TYPE, OpenlhAppletClass))

#define OPENLHCLIENT_DBUS_INTERFACE "org.gnome.OpenlhClient"
#define OPENLHCLIENT_DBUS_PATH "/org/gnome/OpenlhClient"

typedef struct _OpenlhApplet OpenlhApplet;
typedef struct _OpenlhAppletClass OpenlhAppletClass;

struct _OpenlhApplet
{
  GObject       parent;
  GtkBuilder   *builder;
  PanelApplet  *applet;
  GtkWidget    *main_hbox;
  GtkWidget    *prefs;
  GtkWidget    *error_label;
  GtkWidget    *time;
  GtkWidget    *time_elapsed;
  GtkWidget    *time_left;
  GtkWidget    *credit;
  GtkWidget    *total_to_pay;
  GtkWidget    *full_name;
  
  //DBus objects
  DBusGConnection *connection;
  DBusGProxy      *openlh_proxy;
  DBusGProxy      *dbus_proxy;
};

struct _OpenlhAppletClass
{
  GObjectClass parent;
  /* class members */
};

GType openlh_applet_get_type (void);
OpenlhApplet *openlh_applet_new (PanelApplet *applet);

void 
openlh_applet_construct (OpenlhApplet * self);

void 
openlh_applet_get_configs (OpenlhApplet * self);

G_END_DECLS
#endif /* _APPLET_H */
