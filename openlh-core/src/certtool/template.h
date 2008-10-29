/**
* Copyright (C) 2008 N3RD3X <n3rd3x@linuxmail.org>
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

#include <Python.h>

typedef struct {
    PyObject_HEAD
    PyObject *organization;
    PyObject *common_name;
    PyObject *expiration_days;
    PyObject *email;
    PyObject *unit;
    PyObject *locality;
    PyObject *state;
    PyObject *country;
} Template;

PyTypeObject TemplateType;