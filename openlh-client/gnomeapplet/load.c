/**
 * Copyright (C) 2008 Wilson Pinto Júnior <wilsonpjunior@gmail.com>
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
#include <gconf/gconf.h>
#include <gtk/gtk.h>
#include <panel-applet.h>
#include <panel-applet-gconf.h>
#include <bonobo/bonobo-main.h>
#include <bonobo/bonobo-ui-util.h>
#include "applet.h"

static gboolean
applet_fill_cb (PanelApplet *applet,
                const gchar *iid,
                gpointer     data)
{
    if (!g_str_equal (iid, "OAFIID:GNOME_OpenlhClientApplet"))
        return FALSE;

    OpenlhApplet *openlh_applet;
    openlh_applet = openlh_applet_new (applet);
    
    return TRUE;
}

PANEL_APPLET_BONOBO_FACTORY ("OAFIID:GNOME_OpenlhClientApplet_Factory",
                             PANEL_TYPE_APPLET,
                             "openlh-client-applet", "0",
                             applet_fill_cb, NULL);
