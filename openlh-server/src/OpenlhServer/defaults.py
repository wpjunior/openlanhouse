#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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

defaults = {"name": "OpenLanhouse",
            "currency": "US$",
            "listen_port": 4558,
            "use_psyco": False,
            "default_welcome_msg": True,
            "login_suport": True,
            "ticket_suport": False,
            "ticket_size": 8,
            "background": False,
            "logo": False,
            "close_apps": False,
            "close_apps_list": [],
            "db/engine": "sqlite",
            "ui/show_notifications": True,
            "ui/maximized": True,
            "ui/height": 550,
            "ui/width": 800,
            "ui/visible": True,
            "ui/position_x": 0,
            "ui/position_y": 0,
            "ui/machines_columns": ("host", "user", "time", "time_last", "total_to_pay"),
            "ui/users_columns": ("nick" ,"name", "email", "credit"),
            "ui/cash_flow_columns": ("day", "hour", "type", "user", "description", "value"),
            "ui/open_debts_machine_columns": ("day", "hour", "machine", "start_time", "end_time", "user", "value"),
            "ui/open_debts_other_columns": ("day", "hour", "time", "user", "value"),
            "ui/page_selected": 0,
            "ui/show_toolbar": True,
            "ui/show_status_bar": True,
            "ui/show_side_bar": True
            }
