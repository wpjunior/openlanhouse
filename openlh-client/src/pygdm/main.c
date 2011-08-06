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

#include <Python.h>
#include "gdm-logout-action.h"

static PyObject *
supports_logout_action (PyObject *self, PyObject *args, PyObject *keywds);

static PyObject *
set_logout_action (PyObject *self, PyObject *args, PyObject *keywds);

static PyObject *
get_logout_action (PyObject *self);

static PyMethodDef module_methods[] = {
    
    {"supports_logout_action", (PyCFunction) supports_logout_action,
                          METH_VARARGS|METH_KEYWORDS, "Suport Logout action"},
    
    {"set_logout_action", (PyCFunction) set_logout_action,
                          METH_VARARGS|METH_KEYWORDS, "Set logout action"},
    
    {"get_logout_action", (PyCFunction) get_logout_action,
                          METH_NOARGS, "Get logout action"},
    
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initgdm(void) 
{
    PyObject *av;
    int argc, i;
    char **argv;
    
    /* initialise GTK ... */
    av = PySys_GetObject("argv");
    if (av != NULL) {
	if (!PyList_Check(av)) {
	    PyErr_Warn(PyExc_Warning, "ignoring sys.argv: it must be a list of strings");
	    av = NULL;
	} else {
	    argc = PyList_Size(av);
	    for (i = 0; i < argc; i++)
		if (!PyString_Check(PyList_GetItem(av, i))) {
		    PyErr_Warn(PyExc_Warning, "ignoring sys.argv: it must be a list of strings");
		    av = NULL;
		    break;
		}
	}
    }
    if (av != NULL) {
	argv = g_new(char *, argc);
	for (i = 0; i < argc; i++)
	    argv[i] = g_strdup(PyString_AsString(PyList_GetItem(av, i)));
    } else {
	    argc = 0;
	    argv = NULL;
    }

    if (!gdk_init_check(&argc, &argv)) {
	if (argv != NULL) {
	    for (i = 0; i < argc; i++)
		g_free(argv[i]);
	    g_free(argv);
	}
	PyErr_SetString(PyExc_RuntimeError, "could not open display");
}
    PyObject* m;
    
    m = Py_InitModule3("gdm", module_methods,
                       "Gdm Logout Action Module");

    if (m == NULL)
      return;
    
    PyModule_AddIntConstant(m, "LOGOUT_ACTION_NONE",     GDM_LOGOUT_ACTION_NONE);
    PyModule_AddIntConstant(m, "LOGOUT_ACTION_SHUTDOWN", GDM_LOGOUT_ACTION_SHUTDOWN);
    PyModule_AddIntConstant(m, "LOGOUT_ACTION_REBOOT",   GDM_LOGOUT_ACTION_REBOOT);
    PyModule_AddIntConstant(m, "LOGOUT_ACTION_SUSPEND",  GDM_LOGOUT_ACTION_SUSPEND);
}

static PyObject *
supports_logout_action (PyObject *self, PyObject *args, PyObject *keywds)
{
    int action;
    static char *kwlist[] = {"action", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "i", kwlist, &action))
        return NULL;
    
    if (gdm_supports_logout_action(action))
    {
        Py_INCREF(Py_True);
        return Py_True;
    }
    else
    {
        Py_INCREF(Py_False);
        return Py_False;
    }
}

static PyObject *
set_logout_action (PyObject *self, PyObject *args, PyObject *keywds)
{
    int action;
    static char *kwlist[] = {"action", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "i", kwlist, &action))
        return NULL;
    
    gdm_set_logout_action(action);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
get_logout_action (PyObject *self)
{
    GdmLogoutAction action;
    action = gdm_get_logout_action ();
    
    return Py_BuildValue("i", action);
}
