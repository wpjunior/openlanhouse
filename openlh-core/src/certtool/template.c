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

static void
Template_dealloc (Template * self)
{
    Py_XDECREF(self->organization);
    Py_XDECREF(self->common_name);
    Py_XDECREF(self->expiration_days);
    Py_XDECREF(self->email);
    Py_XDECREF(self->unit);
    Py_XDECREF(self->locality);
    Py_XDECREF(self->state);
    Py_XDECREF(self->country);
  
    self->ob_type->tp_free((PyObject*) self);
}

static PyObject *
Template_get_organization (Template *self, void *closure)
{
    Py_INCREF(self->organization);
    return self->organization;
}

static int
Template_set_organization(Template *self, PyObject *value, void *closure)
{
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the last attribute");
    return -1;
  }
  
  if (! PyString_Check(value)) {
    PyErr_SetString(PyExc_TypeError, "value must be a string");
    return -1;
  }
  
  Py_DECREF(self->organization);
  Py_INCREF(value);
  self->organization = value;
  
  return 0;
}

static PyObject *
Template_get_common_name (Template *self, void *closure)
{
    Py_INCREF(self->common_name);
    return self->common_name;
}

static int
Template_set_common_name(Template *self, PyObject *value, void *closure)
{
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the last attribute");
    return -1;
  }
  
  if (! PyString_Check(value)) {
    PyErr_SetString(PyExc_TypeError, "value must be a string");
    return -1;
  }
  
  Py_DECREF(self->common_name);
  Py_INCREF(value);
  self->common_name = value;
  
  return 0;
}

static PyObject *
Template_get_expiration_days (Template *self, void *closure)
{
    Py_INCREF(self->expiration_days);
    return self->expiration_days;
}

static int
Template_set_expiration_days (Template *self, PyObject *value, void *closure)
{
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the last attribute");
    return -1;
  }
  
  if (! PyInt_Check(value)) {
    PyErr_SetString(PyExc_TypeError, "value must be a int");
    return -1;
  }
  
  Py_DECREF(self->expiration_days);
  Py_INCREF(value);
  self->expiration_days = value;
  
  return 0;
}

static PyObject *
Template_get_email (Template *self, void *closure)
{
    Py_INCREF(self->email);
    return self->email;
}

static int
Template_set_email (Template *self, PyObject *value, void *closure)
{
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the last attribute");
    return -1;
  }
  
  if (! PyString_Check(value)) {
    PyErr_SetString(PyExc_TypeError, "value must be a string");
    return -1;
  }
  
  Py_DECREF(self->email);
  Py_INCREF(value);
  self->email = value;
  
  return 0;
}

static PyObject *
Template_get_unit (Template *self, void *closure)
{
    Py_INCREF(self->unit);
    return self->unit;
}

static int
Template_set_unit (Template *self, PyObject *value, void *closure)
{
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the last attribute");
    return -1;
  }
  
  if (! PyString_Check(value)) {
    PyErr_SetString(PyExc_TypeError, "value must be a string");
    return -1;
  }
  
  Py_DECREF(self->unit);
  Py_INCREF(value);
  self->unit = value;
  
  return 0;
}

static PyObject *
Template_get_locality (Template *self, void *closure)
{
    Py_INCREF(self->locality);
    return self->locality;
}

static int
Template_set_locality (Template *self, PyObject *value, void *closure)
{
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the last attribute");
    return -1;
  }
  
  if (! PyString_Check(value)) {
    PyErr_SetString(PyExc_TypeError, "value must be a string");
    return -1;
  }
  
  Py_DECREF(self->locality);
  Py_INCREF(value);
  self->locality = value;
  
  return 0;
}

static PyObject *
Template_get_state (Template *self, void *closure)
{
    Py_INCREF(self->state);
    return self->state;
}

static int
Template_set_state (Template *self, PyObject *value, void *closure)
{
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the last attribute");
    return -1;
  }
  
  if (! PyString_Check(value)) {
    PyErr_SetString(PyExc_TypeError, "value must be a string");
    return -1;
  }
  
  Py_DECREF(self->state);
  Py_INCREF(value);
  self->state = value;
  
  return 0;
}

static PyObject *
Template_get_country (Template *self, void *closure)
{
    Py_INCREF(self->country);
    return self->country;
}

static int
Template_set_country (Template *self, PyObject *value, void *closure)
{
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the last attribute");
    return -1;
  }
  
  if (! PyString_Check(value)) {
    PyErr_SetString(PyExc_TypeError, "value must be a string");
    return -1;
  }
  
  Py_DECREF(self->country);
  Py_INCREF(value);
  self->country = value;
  
  return 0;
}

static PyObject *
Template_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Template *self;
    
    self = (Template *)type->tp_alloc(type, 0);
    
    if (self != NULL) {
        self->organization = PyString_FromString("");
        self->common_name = PyString_FromString("");
        self->expiration_days = PyLong_FromLong(0);
        self->email = PyString_FromString("");
        self->unit = PyString_FromString("");
        self->locality = PyString_FromString("");
        self->state = PyString_FromString("");
        self->country = PyString_FromString("");
      
        if (self->organization == NULL)
          {
            Py_DECREF(self);
            return NULL;
          }
        
        if (self->common_name == NULL)
          {
            Py_DECREF(self);
            return NULL;
          }
        
        if (self->email == NULL)
          {
            Py_DECREF(self);
            return NULL;
          }
        
        if (self->unit == NULL)
          {
            Py_DECREF(self);
            return NULL;
          }
          
        if (self->locality == NULL)
          {
            Py_DECREF(self);
            return NULL;
          }
          
        if (self->state == NULL)
          {
            Py_DECREF(self);
            return NULL;
          }
          
        if (self->country == NULL)
          {
            Py_DECREF(self);
            return NULL;
          }
    }

    return (PyObject *)self;
}

static PyGetSetDef Template_getseters[] = {
    {"organization", 
     (getter)Template_get_organization, (setter)Template_set_organization,
     "Organization name",
     NULL},
     
     {"common_name", 
     (getter)Template_get_common_name, (setter)Template_set_common_name,
     "Common name",
     NULL},
     
     {"expiration_days", 
     (getter)Template_get_expiration_days, (setter)Template_set_expiration_days,
     "Expiration days",
     NULL},
     
     {"email", 
     (getter)Template_get_email, (setter)Template_set_email,
     "Email name",
     NULL},
     
     {"unit", 
     (getter)Template_get_unit, (setter)Template_set_unit,
     "Unit name",
     NULL},
     
     {"locality", 
     (getter)Template_get_locality, (setter)Template_set_locality,
     "Locality name",
     NULL},
     
     {"state", 
     (getter)Template_get_state, (setter)Template_set_state,
     "State name",
     NULL},
     
     {"country", 
     (getter)Template_get_country, (setter)Template_set_country,
     "Country name",
     NULL},
     
    {NULL}  /* Sentinel */
};

PyTypeObject TemplateType = {
    PyObject_HEAD_INIT(NULL)
    0,                               /*ob_size*/
    "certtool.Template",             /*tp_name*/
    sizeof(Template),                /*tp_basicsize*/
    0,                               /*tp_itemsize*/
    (destructor)Template_dealloc,    /*tp_dealloc*/
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
    "Template objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    0,                   /* tp_methods */
    0,                   /* tp_members */
    Template_getseters,  /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                    /* tp_init */
    0,                         /* tp_alloc */
    Template_new,                 /* tp_new */
};