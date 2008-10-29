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
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <gcrypt.h>
#include <time.h>
#include <gnutls/gnutls.h>
#include <gnutls/x509.h>
#include <gnutls/pkcs12.h>

#include "template.h"
#include "privkey.h"
#include "self-signed.h"

int certtool_quick_random = 1;
unsigned char buffer[64 * 1024];

char *
read_binary_file (const char *filename, size_t * length);

static PyObject *
certtool_load_private_key(PyObject *self, PyObject *args, PyObject *keywds);

static PyObject *
certtool_generate_private_key(PyObject *self, PyObject *args, PyObject *keywds);

static PyObject *
certtool_generate_self_signed(PyObject *self, PyObject *args, PyObject *keywds);

static PyObject *
certtool_get_quick_random(PyObject *self, PyObject *args);

static PyObject *
certtool_set_quick_random(PyObject *self, PyObject *args);

static PyMethodDef module_methods[] = {
    {"load_private_key", (PyCFunction) certtool_load_private_key, 
                          METH_VARARGS|METH_KEYWORDS, "Load private key"},
    
    {"generate_private_key", (PyCFunction) certtool_generate_private_key, 
                          METH_VARARGS|METH_KEYWORDS, "Generate private key"},
    
    {"generate_self_signed", (PyCFunction) certtool_generate_self_signed,
                          METH_VARARGS|METH_KEYWORDS, "Generate self-signed"},
    
    {"get_quick_random", (PyCFunction) certtool_get_quick_random,
                          METH_NOARGS, "Get quick random status"},
    
    {"set_quick_random", (PyCFunction) certtool_set_quick_random,
                          METH_VARARGS, "Set quick random status"},
    
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initcerttool(void) 
{
    PyObject* m;
    
    if (PyType_Ready(&TemplateType) < 0)
        return;
    
    if (PyType_Ready(&PrivKeyType) < 0)
        return;
    
    if (PyType_Ready(&SelfSignedType) < 0)
        return;

    m = Py_InitModule3("certtool", module_methods,
                       "Certtool module");

    if (m == NULL)
      return;
    
    Py_INCREF(&TemplateType);
    Py_INCREF(&PrivKeyType);
    PyModule_AddObject(m, "Template", (PyObject *) &TemplateType);
    //PyModule_AddObject(m, "PrivKey", (PyObject *) &PrivKeyType);
    
    PyModule_AddObject(m, "RSA_KEY", Py_BuildValue("i", GNUTLS_PK_RSA));
    PyModule_AddObject(m, "DSA_KEY", Py_BuildValue("i", GNUTLS_PK_DSA));
    PyModule_AddObject(m, "FMT_DER", Py_BuildValue("i", GNUTLS_X509_FMT_DER));
    PyModule_AddObject(m, "FMT_PEM", Py_BuildValue("i", GNUTLS_X509_FMT_PEM));
    
    PyModule_AddObject(m, "DIG_NULL",   Py_BuildValue("i", GNUTLS_DIG_NULL));
    PyModule_AddObject(m, "DIG_MD5",    Py_BuildValue("i", GNUTLS_DIG_MD5));
    PyModule_AddObject(m, "DIG_SHA1",   Py_BuildValue("i", GNUTLS_DIG_SHA1));
    PyModule_AddObject(m, "DIG_RMD160", Py_BuildValue("i", GNUTLS_DIG_RMD160));
    PyModule_AddObject(m, "DIG_MD2",    Py_BuildValue("i", GNUTLS_DIG_MD2));
    PyModule_AddObject(m, "DIG_SHA256", Py_BuildValue("i", GNUTLS_DIG_SHA256));
    PyModule_AddObject(m, "DIG_SHA384", Py_BuildValue("i", GNUTLS_DIG_SHA384));
    PyModule_AddObject(m, "DIG_SHA512", Py_BuildValue("i", GNUTLS_DIG_SHA512));
    
}

static PyObject *
certtool_load_private_key(PyObject *self, PyObject *args, PyObject *keywds)
{
    char *filename;
    int ret;
    gnutls_datum_t dat;
    PrivKey *key_obj;
    PyObject *file_obj;
    size_t size;
    int format = GNUTLS_X509_FMT_PEM;
    static char *kwlist[] = {"filename", "format", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "s|i", 
                                     kwlist, &filename, &format))
        return NULL;
    
    key_obj = PyObject_New(PrivKey, &PrivKeyType);
    
    if ((ret = gnutls_global_init ()) < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    ret = gnutls_x509_privkey_init (&key_obj->key);
    
    if (ret < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    //READ FILE
    dat.data = read_binary_file (filename, &size);
    dat.size = size;
    
    if (dat.data == NULL) {
      Py_INCREF(PyExc_IOError);
      return PyErr_Format(PyExc_IOError, "Failed to open filename");
    }
    
    ret = gnutls_x509_privkey_import (key_obj->key, &dat, format);
    free (dat.data);
    
    if (ret < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    key_obj->type = format;
    return (PyObject *) key_obj;
}

static PyObject *
certtool_generate_private_key(PyObject *self, PyObject *args, PyObject *keywds)
{
    int type = 1;
    int bits, ret;
    PrivKey *key_obj;
    
    static char *kwlist[] = {"bits", "type", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "i|i", 
                                     kwlist, &bits, &type))
        return NULL; 
    
    key_obj = PyObject_New(PrivKey, &PrivKeyType);
    
    if (certtool_quick_random)
        gcry_control (GCRYCTL_ENABLE_QUICK_RANDOM, 0);
    
    if ((ret = gnutls_global_init ()) < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    if ((type==GNUTLS_PK_DSA)&&(bits > 1024)){
        Py_INCREF(PyExc_ValueError);
        return PyErr_Format(PyExc_ValueError, "dsa is incompatible with bits > 1024");
    }
    
    ret = gnutls_x509_privkey_init (&key_obj->key);
    
    if (ret < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    key_obj->bits = bits;
    
    gnutls_x509_privkey_generate ((gnutls_x509_privkey_t) key_obj->key,
                                  type, bits, 0);
    
    //gnutls_global_deinit ();
    
    return (PyObject *) key_obj;
}

static PyObject *
certtool_generate_self_signed(PyObject *self, PyObject *args, PyObject *keywds)
{
    PrivKey    *key_obj;
    Template   *template_obj;
    SelfSigned *certificate;
    
    int ret;
    gnutls_digest_algorithm_t dig;
    dig = GNUTLS_DIG_MD5;
    
    static char *kwlist[] = {"privkey", "template", "dig", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "OO|i",  kwlist,
                                     &key_obj, &template_obj, &dig))
        return NULL;
    
    if(!PyObject_TypeCheck(key_obj, &PrivKeyType)) {
        Py_INCREF(PyExc_TypeError);
        return PyErr_Format(PyExc_TypeError,
                            "privkey must be a certtool.PrivKey");
    }
    
    if(!PyObject_TypeCheck(template_obj, &TemplateType)) {
        Py_INCREF(PyExc_TypeError);
        return PyErr_Format(PyExc_TypeError,
                            "template must be a certtool.Template");
    }
    
    certificate = PyObject_New(SelfSigned, &SelfSignedType);
    certificate->privkey_obj = (PrivKey *) key_obj;
    certificate->template_obj = (Template *) template_obj;
    
    if ((ret = gnutls_global_init ()) < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    ret = gnutls_x509_crt_init (&certificate->crt);
    
    if (ret < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    //TEMPLATE
    const char *organization = PyString_AsString(template_obj->organization);
    const char *common_name = PyString_AsString(template_obj->common_name);
    const char *email = PyString_AsString(template_obj->email);
    const char *unit = PyString_AsString(template_obj->unit);
    const char *locality = PyString_AsString(template_obj->locality);
    const char *state = PyString_AsString(template_obj->state);
    const char *country = PyString_AsString(template_obj->country);
    
    if (organization[0]!='\0') {
        gnutls_x509_crt_set_dn_by_oid (certificate->crt,
                                       GNUTLS_OID_X520_ORGANIZATION_NAME,
                                       0, organization,
                                       strlen (organization));
    }
    
    if (common_name[0]!='\0') {
        gnutls_x509_crt_set_dn_by_oid (certificate->crt,
                                       GNUTLS_OID_X520_COMMON_NAME,
                                       0, common_name,
                                       strlen (common_name));
    }
    
    if (unit[0]!='\0') {
        gnutls_x509_crt_set_dn_by_oid (certificate->crt,
                                       GNUTLS_OID_X520_ORGANIZATIONAL_UNIT_NAME,
                                       0, unit, strlen (unit));
    }
    
    if (locality[0]!='\0') {
        gnutls_x509_crt_set_dn_by_oid (certificate->crt,
                                       GNUTLS_OID_X520_LOCALITY_NAME,
                                       0, locality,
                                       strlen (locality));
    }
    
    if (state[0]!='\0') {
        gnutls_x509_crt_set_dn_by_oid (certificate->crt,
                                       GNUTLS_OID_X520_STATE_OR_PROVINCE_NAME,
                                       0, state,
                                       strlen (state));
    }
    
    if (country[0]!='\0') {
        gnutls_x509_crt_set_dn_by_oid (certificate->crt,
                                       GNUTLS_OID_X520_COUNTRY_NAME,
                                       0, country,
                                       strlen (country));
    }
    
    //ACTIVATION TIME
    ret = gnutls_x509_crt_set_activation_time (certificate->crt, time (NULL));
    
    if (ret < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    //EXPIRATION DAYS
    
    const int *expiration_days = PyInt_AsLong(template_obj->expiration_days);
    
    ret = gnutls_x509_crt_set_expiration_time (certificate->crt,
                        time (NULL) + (int) expiration_days * 24 * 60 * 60);
    
    if (ret < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    ret = gnutls_x509_crt_set_key ((gnutls_x509_crt_t) certificate->crt,
                                   key_obj->key);
    
    if (ret < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    int serial = time (NULL);
    buffer[4] = serial & 0xff;
    buffer[3] = (serial >> 8) & 0xff;
    buffer[2] = (serial >> 16) & 0xff;
    buffer[1] = (serial >> 24) & 0xff;
    buffer[0] = 0;

    ret = gnutls_x509_crt_set_serial ((gnutls_x509_crt_t) certificate->crt,
                                       buffer, 5);
    
    if (ret < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    ret = gnutls_x509_crt_sign2 ((gnutls_x509_crt_t) certificate->crt, 
                                 (gnutls_x509_crt_t) certificate->crt,
                                 key_obj->key, dig, 0);
    
    if (ret < 0) {
        Py_INCREF(PyExc_SystemError);
        return PyErr_Format(PyExc_SystemError, gnutls_strerror (ret));
    }
    
    return (PyObject *) certificate;
    
}

static PyObject *
certtool_get_quick_random(PyObject *self, PyObject *args)
{
    return PyBool_FromLong(certtool_quick_random);
}

static PyObject *
certtool_set_quick_random(PyObject *self, PyObject *args)
{
    unsigned short int status;
    
    if (!PyArg_ParseTuple(args, "i", &status))
        return NULL;
    
    if (status==0)
        certtool_quick_random = 0;
    else
        certtool_quick_random = 1;
    
    return Py_BuildValue("");

}

/*
 * Copyright (C) 2006 Free Software Foundation, Inc.
 * Written by Simon Josefsson and Bruno Haible.
*/

char *
fread_file (FILE * stream, size_t * length)
{
  char *buf = NULL;
  size_t alloc = 0;
  size_t size = 0;
  int save_errno;

  for (;;)
    {
      size_t count;
      size_t requested;

      if (size + BUFSIZ + 1 > alloc)
	{
	  char *new_buf;

	  alloc += alloc / 2;
	  if (alloc < size + BUFSIZ + 1)
	    alloc = size + BUFSIZ + 1;

	  new_buf = realloc (buf, alloc);
	  if (!new_buf)
	    {
	      save_errno = errno;
	      break;
	    }

	  buf = new_buf;
	}

      requested = alloc - size - 1;
      count = fread (buf + size, 1, requested, stream);
      size += count;

      if (count != requested)
	{
	  save_errno = errno;
	  if (ferror (stream))
	    break;
	  buf[size] = '\0';
	  *length = size;
	  return buf;
	}
    }

  free (buf);
  errno = save_errno;
  return NULL;
}

static char *
internal_read_file (const char *filename, size_t * length, const char *mode)
{
  FILE *stream = fopen (filename, mode);
  char *out;
  int save_errno;

  if (!stream)
    return NULL;

  out = fread_file (stream, length);

  save_errno = errno;

  if (fclose (stream) != 0)
    {
      if (out)
	{
	  save_errno = errno;
	  free (out);
	}
      errno = save_errno;
      return NULL;
    }

  return out;
}

/* Open and read the contents of FILENAME, and return a newly
   allocated string with the content, and set *LENGTH to the length of
   the string.  The string is zero-terminated, but the terminating
   zero byte is not counted in *LENGTH.  On errors, *LENGTH is
   undefined, errno preserves the values set by system functions (if
   any), and NULL is returned.  */
char *
read_file (const char *filename, size_t * length)
{
  return internal_read_file (filename, length, "r");
}

/* Open (on non-POSIX systems, in binary mode) and read the contents
   of FILENAME, and return a newly allocated string with the content,
   and set LENGTH to the length of the string.  The string is
   zero-terminated, but the terminating zero byte is not counted in
   the LENGTH variable.  On errors, *LENGTH is undefined, errno
   preserves the values set by system functions (if any), and NULL is
   returned.  */
char *
read_binary_file (const char *filename, size_t * length)
{
  return internal_read_file (filename, length, "rb");
}

