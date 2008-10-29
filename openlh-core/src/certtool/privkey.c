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
#include <gnutls/x509.h>
#include <stdio.h>

typedef struct {
    PyObject_HEAD
    int                   *bits;
    int                   *type;
    gnutls_x509_privkey_t *key;
} PrivKey;

static PyObject *
privkey_export (PrivKey *self, PyObject *args, PyObject *kwds)
{
    int format = GNUTLS_X509_FMT_PEM, ret;
    unsigned char buffer[10 * 1024]; //TODO
    size_t buffer_size = sizeof (buffer);
    buffer_size = sizeof (buffer);
  
    static char *kwlist[] = {"format", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", 
                                     kwlist, &format))
        return NULL;
    
    ret = gnutls_x509_privkey_export ((gnutls_x509_privkey_t) self->key,
                                      format, buffer, &buffer_size);
    
    if (ret < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    return Py_BuildValue("s", buffer);
}

static void
PrivKey_dealloc (PrivKey * self)
{
    gnutls_x509_privkey_deinit ((gnutls_x509_privkey_t) self->key);
    self->ob_type->tp_free ((PyObject*) self);
}

static PyObject *
PrivKey_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PrivKey *self;
    
    self = (PrivKey *) type->tp_alloc(type, 0);
    
    if (self != NULL) {
        self->bits = 1024;
        self->type = 1;
    }

    return (PyObject *) self;
}

static PyMethodDef privkey_methods[] = {
    {"export", (PyCFunction) privkey_export, 
                METH_VARARGS|METH_KEYWORDS, "Export private key"},
    
    {NULL}  /* Sentinel */
};

PyTypeObject PrivKeyType = {
    PyObject_HEAD_INIT(NULL)
    0,                               /*ob_size*/
    "certtool.PrivKey",             /*tp_name*/
    sizeof(PrivKey),                /*tp_basicsize*/
    0,                               /*tp_itemsize*/
    (destructor)PrivKey_dealloc,    /*tp_dealloc*/
    0,                               /*tp_print*/
    0,                               /*tp_getattr*/
    0,                               /*tp_setattr*/
    0,                               /*tp_compare*/
    0,                               /*tp_repr*/
    0,                               /*tp_as_number*/
    0,                               /*tp_as_sequence*/
    0,                               /*tp_as_mapping*/
    0,                               /*tp_hash */
    0,                               /*tp_call*/
    0,                               /*tp_str*/
    0,                               /*tp_getattro*/
    0,                               /*tp_setattro*/
    0,                               /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "PrivKey object",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    privkey_methods,     /* tp_methods */
    0,                   /* tp_members */
    0,                   /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    PrivKey_new,                 /* tp_new */
};