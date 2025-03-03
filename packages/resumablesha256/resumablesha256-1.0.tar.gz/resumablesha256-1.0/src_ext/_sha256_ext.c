/*********************************************************************
* Filename:   _sha256_ext.c
* Author:     Luke Moore
* Project:    https://github.com/luke-moore/resumablesha256/
* License:
    This is free and unencumbered software released into the public domain.

    Anyone is free to copy, modify, publish, use, compile, sell, or
    distribute this software, either in source code form or as a compiled
    binary, for any purpose, commercial or non-commercial, and by any
    means.

    In jurisdictions that recognize copyright laws, the author or authors
    of this software dedicate any and all copyright interest in the
    software to the public domain. We make this dedication for the benefit
    of the public at large and to the detriment of our heirs and
    successors. We intend this dedication to be an overt act of
    relinquishment in perpetuity of all present and future rights to this
    software under copyright law.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
    OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.

    For more information, please refer to <https://unlicense.org>
*********************************************************************/

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "bcon_sha256.h"

typedef struct {
    PyObject_HEAD
    SHA256_CTX ctx;
} SHA256Object;


static PyObject *
resumablesha256_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    SHA256Object *self;
    self = (SHA256Object *)type->tp_alloc(type, 0);
    if (self != NULL) {
        sha256_init(&self->ctx);

        PyObject *initial = NULL;
        if (!PyArg_ParseTuple(args, "|O", &initial)) {
            Py_DECREF(self);
            return NULL;
        }
        if (initial) {
            if (!PyBytes_Check(initial)) {
                PyErr_SetString(PyExc_TypeError,
                    "Strings must be encoded before hashing");
                Py_DECREF(self);
                return NULL;
            }

            char *data;
            Py_ssize_t len;
            if (PyBytes_AsStringAndSize(initial, &data, &len) < 0) {
                Py_DECREF(self);
                return NULL;
            }
            sha256_update(&self->ctx, (const unsigned char *)data, (size_t)len);
	}
    }
    return (PyObject *)self;
}

static void
resumablesha256_dealloc(SHA256Object *self)
{
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
resumablesha256_update(SHA256Object *self, PyObject *args)
{
    const char *data;
    Py_ssize_t len;

    if (!PyArg_ParseTuple(args, "s#", &data, &len))
        return NULL;
    sha256_update(&self->ctx, (const unsigned char *)data, (size_t)len);
    Py_RETURN_NONE;
}

static PyObject *
resumablesha256_digest(SHA256Object *self, PyObject *Py_UNUSED(ignored))
{
    // Create a copy of the context so that we don’t change the state.
    unsigned char hash[32];
    SHA256_CTX temp = self->ctx;
    sha256_final(&temp, hash);
    return Py_BuildValue("y#", hash, 32);
}

static PyObject *
resumablesha256_hexdigest(SHA256Object *self, PyObject *Py_UNUSED(ignored))
{
    unsigned char hash[32];
    char hex_output[65];
    SHA256_CTX temp = self->ctx;
    sha256_final(&temp, hash);
    for (int i = 0; i < 32; i++) {
        sprintf(hex_output + (i * 2), "%02x", hash[i]);
    }
    hex_output[64] = '\0';
    return Py_BuildValue("s", hex_output);
}

static PyObject *
resumablesha256_getstate(SHA256Object *self, PyObject *Py_UNUSED(ignored))
{
    return PyBytes_FromStringAndSize(
        (const char *)&self->ctx, sizeof(SHA256_CTX));
}

static PyObject *
resumablesha256_setstate(SHA256Object *self, PyObject *state)
{
    char *buf;
    Py_ssize_t len;
    if (PyBytes_AsStringAndSize(state, &buf, &len) < 0) {
        return NULL;
    }
    if (len != sizeof(SHA256_CTX)) {
        PyErr_SetString(PyExc_ValueError, "Invalid state length");
        return NULL;
    }
    memcpy(&self->ctx, buf, sizeof(SHA256_CTX));
    Py_RETURN_NONE;
}

static PyObject *
resumablesha256_copy(SHA256Object *self, PyObject *Py_UNUSED(ignored))
{
    SHA256Object *new_obj = PyObject_New(SHA256Object, Py_TYPE(self));
    if (new_obj == NULL)
        return NULL;
    memcpy(&new_obj->ctx, &self->ctx, sizeof(SHA256_CTX));
    return (PyObject *)new_obj;
}

static PyObject *
resumablesha256_get_digest_size(SHA256Object *self, void *closure)
{
    return PyLong_FromLong(32);
}

static PyObject *
resumablesha256_get_block_size(SHA256Object *self, void *closure)
{
    return PyLong_FromLong(64);
}

static PyObject *
resumablesha256_get_name(SHA256Object *self, void *closure)
{
    return PyUnicode_FromString("sha256");
}

static PyGetSetDef resumablesha256_getsetters[] = {
    {"digest_size", (getter)resumablesha256_get_digest_size, NULL,
        "digest size", NULL},
    {"block_size",  (getter)resumablesha256_get_block_size, NULL,
        "block size", NULL},
    {"name", (getter)resumablesha256_get_name, NULL,
        "hash name", NULL},
    {NULL}
};

static PyMethodDef resumablesha256_methods[] = {
    {"update", (PyCFunction)resumablesha256_update, METH_VARARGS,
        "Update the hash with data"},
    {"digest", (PyCFunction)resumablesha256_digest, METH_NOARGS,
        "Return the binary digest"},
    {"hexdigest", (PyCFunction)resumablesha256_hexdigest, METH_NOARGS,
        "Return the hexadecimal digest"},
    {"__getstate__", (PyCFunction)resumablesha256_getstate, METH_NOARGS,
        "Return internal state for pickling"},
    {"__setstate__", (PyCFunction)resumablesha256_setstate, METH_O,
        "Restore internal state from pickled data"},
    {"copy", (PyCFunction)resumablesha256_copy, METH_NOARGS,
        "Return a copy of the hash object"},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject SHA256Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "resumablesha256.sha256",
    .tp_doc = "Resumable sha256 hash objects",
    .tp_basicsize = sizeof(SHA256Object),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = resumablesha256_new,
    .tp_dealloc = (destructor)resumablesha256_dealloc,
    .tp_methods = resumablesha256_methods,
    .tp_getset = resumablesha256_getsetters,
};

static PyModuleDef resumablesha256module = {
    PyModuleDef_HEAD_INIT,
    "resumablesha256_ext",
    "An SHA-256 implementation whose state can be saved and loaded",
    -1,
    NULL, NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__sha256_ext(void)
{
    PyObject *m;
    if (PyType_Ready(&SHA256Type) < 0)
        return NULL;

    m = PyModule_Create(&resumablesha256module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&SHA256Type);
    if (PyModule_AddObject(m, "sha256", (PyObject *)&SHA256Type) < 0) {
        Py_DECREF(&SHA256Type);
        Py_DECREF(m);
        return NULL;
    }
    return m;
}
