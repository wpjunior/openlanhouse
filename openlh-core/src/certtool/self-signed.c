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
#include "privkey.h"
#include "template.h"

typedef struct {
    PyObject_HEAD
    PrivKey               *privkey_obj;
    Template              *template_obj;
    gnutls_x509_crt_t     *crt;
} SelfSigned;


static PyObject *
self_signed_export (SelfSigned *self, PyObject *args, PyObject *kwds)
{
    int format = GNUTLS_X509_FMT_PEM, ret;
    unsigned char buffer[64 * 1024];
    size_t buffer_size = sizeof (buffer);
    
    static char *kwlist[] = {"format", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", 
                                     kwlist, &format))
        return NULL;
    
    ret = gnutls_x509_crt_export ((gnutls_x509_crt_t) self->crt,
                                  format, buffer, &buffer_size);
    
    if (ret < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    return Py_BuildValue("s", buffer);
}

static void
SelfSigned_dealloc (SelfSigned * self)
{
    //gnutls_x509_privkey_deinit ((gnutls_x509_privkey_t) self->key);
    self->ob_type->tp_free ((PyObject*) self);
}

static PyObject *
SelfSigned_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    SelfSigned *self;
    
    self = (SelfSigned *) type->tp_alloc(type, 0);
    
    /*if (self != NULL) {
        self->bits = 1024;
        self->type = 1;
    }*/

    return (PyObject *) self;
}

static PyObject *
self_signed_get_template(SelfSigned *self)
{
    return (PyObject *) self->template_obj;
}

static PyObject *
self_signed_get_privkey(SelfSigned *self)
{
    return (PyObject *) self->privkey_obj;
}

static PyMethodDef selfsigned_methods[] = {
    {"export", (PyCFunction) self_signed_export, 
                METH_VARARGS|METH_KEYWORDS, "Export self-signed certificate"},
    
    {"get_template", (PyCFunction) self_signed_get_template, 
                METH_NOARGS, "Get self-signed template"},
    
    {"get_privkey", (PyCFunction) self_signed_get_privkey, 
                METH_NOARGS, "Get self-signed privkey"},
  
    {NULL}  /* Sentinel */
};

PyTypeObject SelfSignedType = {
    PyObject_HEAD_INIT(NULL)
    0,                               /*ob_size*/
    "certtool.SelfSigned",             /*tp_name*/
    sizeof(SelfSigned),                /*tp_basicsize*/
    0,                               /*tp_itemsize*/
    (destructor)SelfSigned_dealloc,    /*tp_dealloc*/
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
    "SelfSigned object",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    selfsigned_methods,     /* tp_methods */
    0,                   /* tp_members */
    0,                   /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    SelfSigned_new,                 /* tp_new */
};