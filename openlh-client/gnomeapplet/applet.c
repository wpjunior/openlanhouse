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

#include <config.h>
#include <glib/gi18n.h>
#include <glib.h>

#include "applet.h"

const gchar *authors[] = {
    "Wilson Pinto Júnior <wilson@openlanhouse.org>",
    NULL
};

const gchar *widget_titles[] = {
    "username_title",
    "credit_title",
    "time_title",
    "elapsed_title",
    "left_title",
    "total_to_pay_title",
    NULL
};

static void openlh_applet_class_init (OpenlhAppletClass * klass);
static void openlh_applet_init (OpenlhApplet * self);

static void cb_verb (BonoboUIComponent *uic,
                     OpenlhApplet      *self,
                     const gchar       *verbname);

static void builder_connect_handler (GtkBuilder     *builder,
                                     GObject        *object,
                                     const gchar    *signal_name,
                                     const gchar    *handler_name,
                                     GObject        *connect_object,
                                     GConnectFlags   flags,
                                     OpenlhApplet   *self);

static void
on_prefs_close_clicked (GtkButton *close_button, OpenlhApplet *self);

static void
applet_change_background_cb (PanelApplet               *applet,
                             PanelAppletBackgroundType  type,
                             GdkColor                  *color,
                             GdkPixmap                 *pixmap,
                             OpenlhApplet              *self);

static void
on_prefs_show_titles_toggled (GtkCheckButton           *widget,
                              OpenlhApplet             *self);

static void
on_prefs_show_username_toggled (GtkCheckButton           *widget,
                                OpenlhApplet             *self);

static void
on_prefs_show_credit_toggled (GtkCheckButton           *widget,
                              OpenlhApplet             *self);

static void
on_prefs_show_time_toggled (GtkCheckButton           *widget,
                            OpenlhApplet             *self);

static void
on_prefs_show_elapsed_toggled (GtkCheckButton           *widget,
                               OpenlhApplet             *self);

static void
on_prefs_show_left_toggled (GtkCheckButton           *widget,
                            OpenlhApplet             *self);

static void
on_prefs_show_total_to_pay_toggled (GtkCheckButton           *widget,
                                    OpenlhApplet             *self);

static void
openlh_client_applet_free (OpenlhApplet *self);

GType
openlh_applet_get_type (void)
{
  static GType openlh_applet_type = 0;

  if (openlh_applet_type == 0)
    {
      openlh_applet_type = g_type_register_static_simple (G_TYPE_OBJECT,
                                                          "OpenlhApplet",
                                                          sizeof (OpenlhAppletClass),
                                                          (GClassInitFunc)
                                                          openlh_applet_class_init,
                                                          sizeof (OpenlhApplet),
                                                          (GInstanceInitFunc)
                                                          openlh_applet_init, 0);
    }
  return openlh_applet_type;
}

static void
openlh_applet_class_init (OpenlhAppletClass * klass)
{
  // to keep compilation errors so far...
  klass = OPENLH_APPLET_CLASS (klass);
}

static void
openlh_applet_init (OpenlhApplet * self)
{
  self = OPENLH_APPLET (self);
}

static void
openlh_applet_set (OpenlhApplet * self, PanelApplet *applet)
{
    self->applet = applet;
    openlh_applet_construct (self);
}

OpenlhApplet *
openlh_applet_new (PanelApplet *applet)
{
  OpenlhApplet *obj;
  
  obj = g_object_new (OPENLH_APPLET_TYPE, NULL);
  openlh_applet_set (obj, applet);
  return obj;
}

void 
openlh_applet_get_configs (OpenlhApplet * self)
{
    gboolean state;
    GError *error = NULL;
    
    /*Show Titles*/
    state = panel_applet_gconf_get_bool ((PanelApplet *) self->applet,
                                         "show_titles",
                                          &error);
    
    if (error!=NULL)
    {
        g_error (error->message);
        g_error_free (error);
        error = NULL;
    }
    
    guint i;
    GtkWidget *title_widget;
    
    for (i=0; widget_titles[i]; i++)
    {
        title_widget = (GtkWidget *) gtk_builder_get_object (self->builder, 
                                                             widget_titles[i]);
        if (state)
            gtk_widget_show (title_widget);
        else
            gtk_widget_hide (title_widget);
    }
    
    gtk_toggle_button_set_active ((GtkToggleButton *) gtk_builder_get_object (
                                  self->builder, "show_titles"),
                                  state);
    
    /*Show Widgets*/
    /*(Widget, Config), (Applet Widget)*/
    gchar *fields[][2] = {
        {"show_username", "username_hbox"},
        {"show_credit", "credit_hbox"},
        {"show_time", "time_hbox"},
        {"show_time_elapsed", "elapsed_hbox"},
        {"show_time_left", "time_left_hbox"},
        {"show_total_to_pay", "total_to_pay_hbox"},
        {NULL, NULL}
    };
    
    for (i=0; fields[i][0]!=NULL; i++)
    {
        state = panel_applet_gconf_get_bool ((PanelApplet *) self->applet,
                                              fields[i][0],
                                              &error);
    
        if (error!=NULL)
        {
            g_error(error->message);
            g_error_free (error);
            error = NULL;
        }
    
        if (!state)
        {
            gtk_widget_hide ((GtkWidget *) gtk_builder_get_object (
                             self->builder, fields[i][1]));
        }
    
        gtk_toggle_button_set_active ((GtkToggleButton *) gtk_builder_get_object (
                                      self->builder, fields[i][0]),
                                      state);
    }
}

void
openlhapplet_set_registred (OpenlhApplet *self,
                            gboolean      registred)
{
    GtkWidget *username_hbox, *show_username, *credit_hbox, *show_credit;
    GtkWidget *total_to_pay_hbox, *show_total_to_pay;
    
    gboolean state;
    GError *error = NULL;
    
    state = panel_applet_gconf_get_bool ((PanelApplet *) self->applet,
                                         "show_username",
                                          &error);
    
    if (error!=NULL)
    {
        g_error(error->message);
        g_error_free (error);
        error = NULL;
    }
  
    username_hbox = (GtkWidget *) gtk_builder_get_object (
                                   self->builder, "username_hbox");
    show_username = (GtkWidget *) gtk_builder_get_object (
                                   self->builder, "show_username");
    
    if ((registred)&&(state))
        gtk_widget_show (username_hbox);
    else
        gtk_widget_hide (username_hbox);
    
    gtk_widget_set_sensitive (show_username, registred);
    
    //Credit
    error = NULL;
    
    state = panel_applet_gconf_get_bool ((PanelApplet *) self->applet,
                                         "show_credit",
                                          &error);
    
    if (error!=NULL)
    {
        g_error(error->message);
        g_error_free (error);
        error = NULL;
    }
  
    credit_hbox = (GtkWidget *) gtk_builder_get_object (
                                   self->builder, "credit_hbox");
    show_credit = (GtkWidget *) gtk_builder_get_object (
                                   self->builder, "show_credit");
    
    if ((registred)&&(state))
        gtk_widget_show (credit_hbox);
    else
        gtk_widget_hide (credit_hbox);
    
    gtk_widget_set_sensitive (show_credit, registred);
    
    //Total to Pay
    error = NULL;
    
    state = panel_applet_gconf_get_bool ((PanelApplet *) self->applet,
                                         "show_total_to_pay",
                                          &error);
    
    if (error!=NULL)
    {
        g_error(error->message);
        g_error_free (error);
        error = NULL;
    }
  
    total_to_pay_hbox = (GtkWidget *) gtk_builder_get_object (
                                   self->builder, "total_to_pay_hbox");
    show_total_to_pay = (GtkWidget *) gtk_builder_get_object (
                                   self->builder, "show_total_to_pay");
    
    if ((!registred)&&(state))
        gtk_widget_show (total_to_pay_hbox);
    else
        gtk_widget_hide (total_to_pay_hbox);
    
    if (registred)
        gtk_widget_set_sensitive (show_total_to_pay, FALSE);
    else
        gtk_widget_set_sensitive (show_total_to_pay, TRUE);
}

void
openlhapplet_set_limited (OpenlhApplet *self,
                          gboolean      limited)
{
    GtkWidget *time_left_hbox, *show_time_left, *time_hbox, *show_time;
    gboolean state;
    GError *error = NULL;
    
    state = panel_applet_gconf_get_bool ((PanelApplet *) self->applet,
                                         "show_time_left",
                                          &error);
    
    if (error!=NULL)
    {
        g_error(error->message);
        g_error_free (error);
        error = NULL;
    }
  
    time_left_hbox = (GtkWidget *) gtk_builder_get_object (
                                   self->builder, "time_left_hbox");
    show_time_left = (GtkWidget *) gtk_builder_get_object (
                                   self->builder, "show_time_left");
    
    if ((limited)&&(state))
        gtk_widget_show (time_left_hbox);
    else
        gtk_widget_hide (time_left_hbox);
    
    gtk_widget_set_sensitive (show_time_left, limited);
    
    //TIME
    error = NULL;
    
    state = panel_applet_gconf_get_bool ((PanelApplet *) self->applet,
                                         "show_time",
                                          &error);
    
    if (error!=NULL)
    {
        g_error(error->message);
        g_error_free (error);
        error = NULL;
    }
    
    time_hbox = (GtkWidget *) gtk_builder_get_object (
                                   self->builder, "time_hbox");
    show_time = (GtkWidget *) gtk_builder_get_object (
                                   self->builder, "show_time");
    
    if ((limited)&&(state))
        gtk_widget_show (time_hbox);
    else
        gtk_widget_hide (time_hbox);
    
    gtk_widget_set_sensitive (show_time, limited);
}

/*Utils*/
void
humanize_time (guint *mtime,
               guint **hour,
               guint **minutes,
               guint **seconds)
{
    *seconds = ((int) mtime) % 60;
    *minutes = ((int) mtime / 60) % 60;
    *hour = ((int) mtime / (60 * 60)) % 60;
}
/*end utils*/

/*Openlh Client Signals*/
void
on_openlh_client_time_changed (DBusGProxy    *proxy,
                               GArray        *time_array, 
                               OpenlhApplet  *self)
{
    g_assert (time_array->len==2);
    gint *hour, *minutes;
    hour = (gint *) g_array_index (time_array, gint, 0);
    minutes = (gint *) g_array_index (time_array, gint, 1);
    
    gtk_label_set_text ((GtkLabel *) self->time,
                        g_strdup_printf ("%0.2d:%0.2d", hour, minutes));
}

void
on_openlh_client_elapsed_time_changed (DBusGProxy    *proxy,
                                       guint         *elapsed_time, 
                                       OpenlhApplet  *self)
{
    guint *hour, *minutes, *seconds;
    humanize_time (elapsed_time, &hour, &minutes, &seconds);
    gtk_label_set_text ((GtkLabel *) self->time_elapsed,
                        g_strdup_printf ("%0.2d:%0.2d:%0.2d", hour, 
                        minutes, seconds));
}

void
on_openlh_client_left_time_changed (DBusGProxy    *proxy,
                                    guint         *left_time, 
                                    OpenlhApplet  *self)
{
    guint *hour, *minutes, *seconds;
    humanize_time (left_time, &hour, &minutes, &seconds);
    gtk_label_set_text ((GtkLabel *) self->time_left,
                        g_strdup_printf ("%0.2d:%0.2d:%0.2d", hour, 
                        minutes, seconds));
}

void
on_openlh_client_credit_changed (DBusGProxy    *proxy,
                                 const gchar   *credit, 
                                 OpenlhApplet  *self)
{
    gtk_label_set_text ((GtkLabel *) self->credit,
                        credit);
}

void
on_openlh_client_total_to_pay_changed (DBusGProxy    *proxy,
                                       const gchar   *total_to_pay, 
                                       OpenlhApplet  *self)
{
    gtk_label_set_text ((GtkLabel *) self->total_to_pay,
                        total_to_pay);
}

void
on_openlh_client_full_name_changed (DBusGProxy    *proxy,
                                    const gchar   *full_name, 
                                    OpenlhApplet  *self)
{
    if (!g_str_equal (full_name, ""))
    {
        gtk_label_set_text ((GtkLabel *) self->full_name,
                            full_name);
    }
}

void
on_openlh_client_reset_fields (OpenlhApplet *self)
{
    void *fields[] = {
        self->time,
        self->time_elapsed,
        self->time_left,
        self->credit,
        self->total_to_pay,
        self->full_name,
        NULL
    };

    guint i;
    
    for (i=0; fields[i]; i++)
    {
        gtk_label_set_text ((GtkLabel *) fields[i], "");
    }
}

void
on_openlh_client_unblock (DBusGProxy    *proxy,
                          GArray        *array, 
                          OpenlhApplet  *self)
{
    on_openlh_client_reset_fields (self);

    gint *registred, *limited;
    registred = (gint *) g_array_index (array, gint, 0);
    limited = (gint *) g_array_index (array, gint, 1);
    openlhapplet_set_registred (self, (gboolean) registred);
    openlhapplet_set_limited (self, (gboolean) limited);
}

void
on_openlh_client_block   (DBusGProxy    *proxy,
                          OpenlhApplet  *self)
{
    on_openlh_client_reset_fields (self);
}

/*End Openlh Client Signals*/

void
on_dbus_service_connected (OpenlhApplet  *self)
{
    GError *error;
    GList *list = NULL;
    list = gtk_container_get_children ((GtkContainer *) self->applet);
    
    if (g_list_find ((GList *) list, self->error_label))
    {
        gtk_container_remove ((GtkContainer *) self->applet,
                              self->error_label);
        gtk_container_add ((GtkContainer *) self->applet,
                              self->main_hbox);
    }
    
    error = NULL;
    gint *is_blocked, *is_limited, *is_registred;
    
    if (!dbus_g_proxy_call (self->openlh_proxy, "is_blocked", &error, 
                            G_TYPE_INVALID,
                            G_TYPE_INT, &is_blocked, G_TYPE_INVALID))
    {
        g_warning (error->message);
        g_error_free (error);
    }
    
    if (!dbus_g_proxy_call (self->openlh_proxy, "is_limited", &error, 
                            G_TYPE_INVALID,
                            G_TYPE_INT, &is_limited, G_TYPE_INVALID))
    {
        g_warning (error->message);
        g_error_free (error);
    }
    
    if (!dbus_g_proxy_call (self->openlh_proxy, "is_registred", &error, 
                            G_TYPE_INVALID,
                            G_TYPE_INT, &is_registred, G_TYPE_INVALID))
    {
        g_warning (error->message);
        g_error_free (error);
    }
    
    if ((!is_blocked) && (is_registred))
    {
        error = NULL;
        gchar *credit = "";
    
        if (!dbus_g_proxy_call (self->openlh_proxy, "get_credit_as_string", &error, 
                                G_TYPE_INVALID,
                                G_TYPE_STRING, &credit, G_TYPE_INVALID))
        {
            g_warning (error->message);
            g_error_free (error);
        }
    
        if (!g_str_equal (credit, ""))
        {
            gtk_label_set_text ((GtkLabel *) self->credit,
                            credit);
        }
    
        error = NULL;
        gchar *full_name = "";
    
        if (!dbus_g_proxy_call (self->openlh_proxy, "get_user_full_name", &error, 
                                G_TYPE_INVALID,
                                G_TYPE_STRING, &full_name, G_TYPE_INVALID))
        {
            g_warning (error->message);
            g_error_free (error);
        }
    
        if (!g_str_equal (full_name, ""))
        {
            gtk_label_set_text ((GtkLabel *) self->full_name,
                                full_name);
        }
    }
    
    if ((!is_blocked) && (is_limited))
    {
        error = NULL;
        GArray *time_array;
    
        if (!dbus_g_proxy_call (self->openlh_proxy, "get_time", &error, 
                                G_TYPE_INVALID,
                                DBUS_TYPE_G_INT_ARRAY, &time_array, G_TYPE_INVALID))
        {
            g_warning (error->message);
            g_error_free (error);
        }
        
        g_assert (time_array->len==2);
        gint *hour, *minutes;
        hour = (gint *) g_array_index (time_array, gint, 0);
        minutes = (gint *) g_array_index (time_array, gint, 1);
    
        gtk_label_set_text ((GtkLabel *) self->time,
                            g_strdup_printf ("%0.2d:%0.2d", hour, minutes));
    }
    
    if ((!is_blocked) && (!is_registred))
    {
        error = NULL;
        gchar *total_to_pay = "";
        
        if (!dbus_g_proxy_call (self->openlh_proxy, "get_total_to_pay_as_string",
                                &error, 
                                G_TYPE_INVALID,
                                G_TYPE_STRING, &total_to_pay, G_TYPE_INVALID))
        {
            g_warning (error->message);
            g_error_free (error);
        }
        
        gtk_label_set_text ((GtkLabel *) self->total_to_pay,
                            total_to_pay);
    }
    
    if (!is_blocked)
    {
        openlhapplet_set_limited (self, (gboolean) is_limited);
        openlhapplet_set_registred (self, (gboolean) is_registred);
    }
    
    //Connect Signals
    
    dbus_g_proxy_connect_signal (self->openlh_proxy, 
                                 "time_changed", 
                                 G_CALLBACK(on_openlh_client_time_changed), 
                                 self, NULL);
    
    dbus_g_proxy_connect_signal (self->openlh_proxy, 
                                 "elapsed_time_changed", 
                                 G_CALLBACK(on_openlh_client_elapsed_time_changed), 
                                 self, NULL);
    
    dbus_g_proxy_connect_signal (self->openlh_proxy, 
                                 "left_time_changed", 
                                 G_CALLBACK(on_openlh_client_left_time_changed), 
                                 self, NULL);
    
    dbus_g_proxy_connect_signal (self->openlh_proxy, 
                                 "credit_changed_as_string", 
                                 G_CALLBACK(on_openlh_client_credit_changed), 
                                 self, NULL);
    
    dbus_g_proxy_connect_signal (self->openlh_proxy, 
                                 "total_to_pay_changed_as_string", 
                                 G_CALLBACK(on_openlh_client_total_to_pay_changed), 
                                 self, NULL);
    
    dbus_g_proxy_connect_signal (self->openlh_proxy, 
                                 "full_name_changed", 
                                 G_CALLBACK(on_openlh_client_full_name_changed), 
                                 self, NULL);
    
    dbus_g_proxy_connect_signal (self->openlh_proxy, 
                                 "unblock", 
                                 G_CALLBACK(on_openlh_client_unblock), 
                                 self, NULL);
    
    dbus_g_proxy_connect_signal (self->openlh_proxy, 
                                 "block", 
                                 G_CALLBACK(on_openlh_client_block), 
                                 self, NULL);
}

void
disconnect_signals (OpenlhApplet *self)
{
    /*Disconnect Signals*/
    dbus_g_proxy_disconnect_signal (self->openlh_proxy, 
                                    "time_changed", 
                                    G_CALLBACK(on_openlh_client_time_changed), 
                                    self);
    
    dbus_g_proxy_disconnect_signal (self->openlh_proxy, 
                                    "elapsed_time_changed", 
                                    G_CALLBACK(on_openlh_client_elapsed_time_changed), 
                                    self);
    
    dbus_g_proxy_disconnect_signal (self->openlh_proxy, 
                                    "left_time_changed", 
                                    G_CALLBACK(on_openlh_client_left_time_changed), 
                                    self);
    
    dbus_g_proxy_disconnect_signal (self->openlh_proxy, 
                                    "credit_changed_as_string", 
                                    G_CALLBACK(on_openlh_client_credit_changed), 
                                    self);
    
    dbus_g_proxy_disconnect_signal (self->openlh_proxy, 
                                    "total_to_pay_changed_as_string", 
                                    G_CALLBACK(on_openlh_client_total_to_pay_changed), 
                                    self);
    
    dbus_g_proxy_disconnect_signal (self->openlh_proxy, 
                                    "full_name_changed", 
                                    G_CALLBACK(on_openlh_client_full_name_changed), 
                                    self);
    
    dbus_g_proxy_disconnect_signal (self->openlh_proxy, 
                                    "unblock", 
                                    G_CALLBACK(on_openlh_client_unblock), 
                                    self);
    
    dbus_g_proxy_disconnect_signal (self->openlh_proxy, 
                                    "block", 
                                    G_CALLBACK(on_openlh_client_block), 
                                    self);
}

void
on_dbus_service_disconnected (OpenlhApplet  *self)
{
    GList *list = NULL;
    list = gtk_container_get_children ((GtkContainer *) self->applet);
    
    if (g_list_find ((GList *) list, self->main_hbox))
    {
        gtk_container_remove ((GtkContainer *) self->applet,
                              self->main_hbox);
        gtk_container_add ((GtkContainer *) self->applet,
                              self->error_label);
    }
    
    disconnect_signals (self);
}

void
on_dbus_name_owner_changed (DBusGProxy    *proxy,
                            const gchar   *name, 
                            const gchar   *old_owner, 
                            const gchar   *new_owner, 
                            OpenlhApplet  *self)
{
    if (!g_str_equal (name, OPENLHCLIENT_DBUS_INTERFACE))
        return;
    
    if (!g_str_equal (new_owner, ""))
        on_dbus_service_connected (self);
    else
        on_dbus_service_disconnected (self);
}

void
openlh_applet_setup_dbus (OpenlhApplet * self)
{
    GError *error = NULL;
    self->connection = dbus_g_bus_get (DBUS_BUS_SESSION,
                                       &error);
  
    if (self->connection == NULL)
    {
        g_error (N_("Failed to open connection to bus: %s\n"),
                    error->message);
        g_error_free (error);
        return;
    }
    
    self->dbus_proxy = dbus_g_proxy_new_for_name ((DBusGConnection *) self->connection,
                                                  DBUS_SERVICE_DBUS,
                                                  DBUS_PATH_DBUS,
                                                  DBUS_INTERFACE_DBUS);
    
    self->openlh_proxy = dbus_g_proxy_new_for_name ((DBusGConnection *) self->connection,
                                                    OPENLHCLIENT_DBUS_INTERFACE,
                                                    OPENLHCLIENT_DBUS_PATH,
                                                    OPENLHCLIENT_DBUS_INTERFACE);
    
    dbus_g_proxy_add_signal (self->openlh_proxy,
                             "time_changed", 
                             DBUS_TYPE_G_INT_ARRAY,
                             G_TYPE_INVALID);
    
    dbus_g_proxy_add_signal (self->openlh_proxy,
                             "elapsed_time_changed", 
                             G_TYPE_UINT,
                             G_TYPE_INVALID);
    
    dbus_g_proxy_add_signal (self->openlh_proxy,
                             "left_time_changed", 
                             G_TYPE_UINT,
                             G_TYPE_INVALID);
    
    dbus_g_proxy_add_signal (self->openlh_proxy,
                             "credit_changed_as_string", 
                             G_TYPE_STRING,
                             G_TYPE_INVALID);
    
    dbus_g_proxy_add_signal (self->openlh_proxy,
                             "total_to_pay_changed_as_string", 
                             G_TYPE_STRING,
                             G_TYPE_INVALID);
    
    dbus_g_proxy_add_signal (self->openlh_proxy,
                             "full_name_changed", 
                             G_TYPE_STRING,
                             G_TYPE_INVALID);
    
    dbus_g_proxy_add_signal (self->openlh_proxy,
                             "unblock", 
                             DBUS_TYPE_G_INT_ARRAY,
                             G_TYPE_INVALID);
    
    dbus_g_proxy_add_signal (self->openlh_proxy,
                             "block",
                             G_TYPE_INVALID);
    
    gchar **listnames;
    gchar **listnames_ptr;
    error = NULL;
    
    if (!dbus_g_proxy_call (self->dbus_proxy, "ListNames", &error, G_TYPE_INVALID,
                            G_TYPE_STRV, &listnames, G_TYPE_INVALID))
    {
        g_error (error->message);
        g_error_free (error);
        return;
    }
    
    for (listnames_ptr = listnames; *listnames_ptr; listnames_ptr++)
    {
        if (g_str_equal (OPENLHCLIENT_DBUS_INTERFACE, *listnames_ptr))
        {
            on_dbus_service_connected (self);
            break;
        }
    }
    
    g_strfreev (listnames);
    
    dbus_g_proxy_add_signal (self->dbus_proxy,
                             "NameOwnerChanged", 
                             G_TYPE_STRING, G_TYPE_STRING, 
                             G_TYPE_STRING, G_TYPE_INVALID);
    
    dbus_g_proxy_connect_signal (self->dbus_proxy, 
                                 "NameOwnerChanged", 
                                 G_CALLBACK(on_dbus_name_owner_changed), 
                                 self, NULL);
}

void
openlh_applet_construct (OpenlhApplet * self)
{
    GError *error = NULL;
    
    panel_applet_add_preferences ((PanelApplet *) self->applet,
                                  "/schemas/apps/openlh-client-applet/per-applet",
                                  &error);
    
    if (error != NULL)
    {
        g_error (error->message);
    }
    
    self->builder = gtk_builder_new ();
    gtk_builder_add_from_file ((GtkBuilder *) self->builder,
                                     DATADIR "/OpenlhClient/ui/applet.ui",
                                     &error);
    
    if (error != NULL)
    {
        g_error (error->message);
    }
    
    self->main_hbox = (GtkWidget *) gtk_builder_get_object (self->builder, 
                                                            "main_hbox");
    
    self->time = (GtkWidget *) gtk_builder_get_object (self->builder, 
                                                       "time");
    self->time_elapsed = (GtkWidget *) gtk_builder_get_object (self->builder, 
                                                       "elapsed");
    self->time_left = (GtkWidget *) gtk_builder_get_object (self->builder, 
                                                       "left");
    self->credit = (GtkWidget *) gtk_builder_get_object (self->builder, 
                                                       "credit");
    self->total_to_pay = (GtkWidget *) gtk_builder_get_object (self->builder, 
                                                       "total_to_pay");
    self->full_name = (GtkWidget *) gtk_builder_get_object (self->builder, 
                                                       "username");
    
    self->prefs = (GtkWidget *) gtk_builder_get_object (self->builder, 
                                                        "dialog");
    
    GtkWidget *window;
    window = (GtkWidget *) gtk_builder_get_object (self->builder, 
                                                   "window");
    
    gtk_container_remove ((GtkContainer *) window,
                          self->main_hbox);
    
    self->error_label = gtk_label_new (N_("OpenLanhouse Client is Unavailable"));
    g_object_ref (self->error_label);
    
    gtk_container_add ((GtkContainer *) self->applet,
                       self->error_label);
    gtk_widget_show ((GtkWidget *) self->error_label);
    
    /*Menu*/
    static const BonoboUIVerb verbs[] = {
        BONOBO_UI_UNSAFE_VERB ("Help",     cb_verb),
        BONOBO_UI_UNSAFE_VERB ("About",    cb_verb),
        BONOBO_UI_UNSAFE_VERB ("Pref",     cb_verb),
        BONOBO_UI_VERB_END
    };
  
    panel_applet_setup_menu_from_file (PANEL_APPLET (self->applet), 
                                       DATADIR "/gnome-2.0/ui",
                                       "GNOME_OpenlhApplet.xml",
                                       NULL, verbs, self);
    
    openlh_applet_get_configs (self);
    
    g_signal_connect (self->applet, "change-background",
                      G_CALLBACK (applet_change_background_cb), self);
    
    g_object_set_data_full (G_OBJECT (self->applet), "openlh-client-data", self,
          (GDestroyNotify) openlh_client_applet_free);
    
    gtk_widget_show ((GtkWidget *) self->applet);
    
    gtk_builder_connect_signals_full ((GtkBuilder *) self->builder,
                                      (GtkBuilderConnectFunc) builder_connect_handler,
                                      self);
    
    openlh_applet_setup_dbus (self);
}

static void
cb_verb (BonoboUIComponent *uic,
         OpenlhApplet      *self,
         const gchar       *verbname)
{
    if (g_strrstr (verbname, "About"))
    {
        gtk_show_about_dialog (NULL,
                               "program-name", N_("OpenLanhouse Applet"),
                               "comments", N_("Gnome Applet for OpenLanhouse Client"),
                               "copyright", N_("OpenLanhouse - Copyright (c) 2007-2008"),
                               "version", VERSION,
                               "authors", authors,
                               "website", "http://openlanhouse.sf.net",
                               "logo-icon-name", "openlh-client",
                               NULL);
    }
    else if (g_strrstr (verbname, "Pref"))
    {
        gtk_widget_show (self->prefs);
    }
    else if (g_strrstr (verbname, "Help"))
    {
        g_print ("Show Help Dialog\n");
    }
}

void *signals[][2] = 
{
    {"on_prefs_close_clicked", on_prefs_close_clicked},
    {"on_prefs_show_titles_toggled", on_prefs_show_titles_toggled},
    {"on_prefs_show_total_to_pay_toggled", on_prefs_show_total_to_pay_toggled},
    {"on_prefs_show_left_toggled", on_prefs_show_left_toggled},
    {"on_prefs_show_elapsed_toggled", on_prefs_show_elapsed_toggled},
    {"on_prefs_show_time_toggled", on_prefs_show_time_toggled},
    {"on_prefs_show_credit_toggled", on_prefs_show_credit_toggled},
    {"on_prefs_show_username_toggled", on_prefs_show_username_toggled},
    {NULL, NULL}
};

static void
builder_connect_handler (GtkBuilder     *builder,
                         GObject        *object,
                         const gchar    *signal_name,
                         const gchar    *handler_name,
                         GObject        *connect_object,
                         GConnectFlags   flags,
                         OpenlhApplet   *self)
{
    guint i;
    for (i=0; signals[i][0]!=NULL; i++)
        if (g_str_equal (signals[i][0], handler_name))
            g_signal_connect (object, signal_name,
                              G_CALLBACK (signals[i][1]),
                              (gpointer) self);
}

static void
on_prefs_close_clicked (GtkButton *close_button, OpenlhApplet *self)
{
    gtk_widget_hide (self->prefs);
}

static void
change_widget_background (PanelApplet               *applet,
                          PanelAppletBackgroundType  type,
                          GdkColor                  *color,
                          GdkPixmap                 *pixmap,
                          GtkWidget                 *widget)
{
  GtkRcStyle *rc_style;
  GtkStyle   *style;
  
  gtk_widget_set_style (widget, NULL);
  rc_style = gtk_rc_style_new ();
  gtk_widget_modify_style (GTK_WIDGET (widget), rc_style);
  gtk_rc_style_unref (rc_style);

  switch (type)
    {
    case PANEL_NO_BACKGROUND:
      break;
    case PANEL_COLOR_BACKGROUND:
      gtk_widget_modify_bg (widget, GTK_STATE_NORMAL, color);
      break;
    case PANEL_PIXMAP_BACKGROUND:
      style = gtk_style_copy (widget->style);
      if (style->bg_pixmap[GTK_STATE_NORMAL])
        g_object_unref (style->bg_pixmap[GTK_STATE_NORMAL]);

      style->bg_pixmap[GTK_STATE_NORMAL] = g_object_ref (pixmap);
      gtk_widget_set_style (widget, style);
      g_object_unref (style);
      break;
    }
  
  if GTK_IS_BOX (widget)
  {
      GList     *childrens = NULL;
      GtkWidget *children;
      
      childrens = gtk_container_get_children ((GtkContainer *) widget);
      
      if (childrens==NULL)
          return;
      
      guint pos = 0;
      
      for (;;)
      {
          children = g_list_nth_data (childrens, pos);
          if (children==NULL)
              break;
          
          change_widget_background (applet, type, color, pixmap, children);
          pos++;
      }
  }
}

static void
applet_change_background_cb (PanelApplet               *applet,
                             PanelAppletBackgroundType  type,
                             GdkColor                  *color,
                             GdkPixmap                 *pixmap,
                             OpenlhApplet              *self)
{
  change_widget_background (applet, type, color, pixmap, self->main_hbox);
}

static void
on_prefs_show_titles_toggled (GtkCheckButton           *widget,
                              OpenlhApplet             *self)
{
    gboolean state;
    GError *error = NULL;
    
    state = gtk_toggle_button_get_active ((GtkToggleButton *) widget);
  
    panel_applet_gconf_set_bool ((PanelApplet *) self->applet,
                                 "show_titles",
                                 state,
                                 &error);
    
    if (error!=NULL)
    {
        g_error(error->message);
        g_error_free (error);
    }
    
    guint i;
    GtkWidget *title_widget;
    
    for (i=0; widget_titles[i]; i++)
    {
        title_widget = (GtkWidget *) gtk_builder_get_object (self->builder, 
                                                       widget_titles[i]);
        if (state)
            gtk_widget_show (title_widget);
        else
            gtk_widget_hide (title_widget);
    }
}

static void
on_prefs_set_toggled (GtkCheckButton           *widget,
                      OpenlhApplet             *self,
                      const gchar              *gconf_name,
                      const gchar              *applet_widget_name)
{
    gboolean state;
    GError *error = NULL;
    
    state = gtk_toggle_button_get_active ((GtkToggleButton *) widget);
  
    panel_applet_gconf_set_bool ((PanelApplet *) self->applet,
                                 gconf_name, state, &error);
    
    if (error!=NULL)
    {
        g_error(error->message);
        g_error_free (error);
    }
    
    GtkWidget *applet_widget;
    applet_widget = (GtkWidget *) gtk_builder_get_object (self->builder,
                                                          applet_widget_name);
    
    if (state)
        gtk_widget_show (applet_widget);
    else
        gtk_widget_hide (applet_widget);
}

static void
on_prefs_show_username_toggled (GtkCheckButton           *widget,
                                OpenlhApplet             *self)
{
    on_prefs_set_toggled (widget, self, "show_username", "username_hbox");
}

static void
on_prefs_show_credit_toggled (GtkCheckButton           *widget,
                              OpenlhApplet             *self)
{
    on_prefs_set_toggled (widget, self, "show_credit", "credit_hbox");
}

static void
on_prefs_show_time_toggled (GtkCheckButton           *widget,
                            OpenlhApplet             *self)
{
    on_prefs_set_toggled (widget, self, "show_time", "time_hbox");
}

static void
on_prefs_show_elapsed_toggled (GtkCheckButton           *widget,
                               OpenlhApplet             *self)
{
    on_prefs_set_toggled (widget, self, "show_time_elapsed", "elapsed_hbox");
}

static void
on_prefs_show_left_toggled (GtkCheckButton           *widget,
                            OpenlhApplet             *self)
{
    on_prefs_set_toggled (widget, self, "show_time_left", "time_left_hbox");
}

static void
on_prefs_show_total_to_pay_toggled (GtkCheckButton           *widget,
                                    OpenlhApplet             *self)
{
    on_prefs_set_toggled (widget, self, "show_total_to_pay", "total_to_pay_hbox");
}

static void
openlh_client_applet_free (OpenlhApplet *self)
{
    disconnect_signals (self);
    
    if (self->prefs)
        gtk_widget_destroy (self->prefs);
    
    if (self->main_hbox)
        gtk_widget_destroy (self->main_hbox);
    
    g_object_unref (self->builder);
    g_object_unref (self->error_label);
}
