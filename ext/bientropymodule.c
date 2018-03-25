/******************************************************************************
* Copyright 2018 National Technology & Engineering Solutions of Sandia, LLC
* (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
* Government retains certain rights in this software.
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
* ---
*
* This file implements and interface between Python and the C implemntations.
******************************************************************************/

#include <Python.h>
#if PY_MAJOR_VERSION >= 3
#define PyString_Check PyBytes_Check
#define PyString_Size PyBytes_Size
#define PyString_AsString PyBytes_AsString
#endif

#include "bientropy.h"

/** brief bientropy_wrapper - translates parameters from Python, calls C-level
 * function, and translates the return object back into Python. Shared by the
 * bien and tbien functions.
 *
 * param self PyObject* not used
 * param args PyObject* arguments from the Pythin interpreter
 * param f double(*)(mpz_bin) pointer to the C-level function to use
 *
 * return PyObject*
 */
static PyObject *
bientropy_wrapper(PyObject *self, PyObject *args, double (*f)(mpz_bin))
{
    PyObject *in_obj = NULL;
    mpz_bin in;
    PyObject *retval = NULL;
    unsigned int slack;

    // PyArg_ParseTuple returns a borrowed reference for objects
    if (!PyArg_ParseTuple(args, "O", &in_obj))
        return NULL;

    mpz_init(in.i);
    if (PyString_Check(in_obj)) {
        mpz_import(in.i, // rop
                   PyString_Size(in_obj), //count
                   1, // order
                   1, // size
                   1, // endian
                   0, // nails
                   (void*)PyString_AsString(in_obj));
        in.len = PyString_Size(in_obj)*8;
    } else if (PyObject_HasAttrString(in_obj, "tobytes")) {
        PyObject* tobytes_f = PyObject_GetAttrString(in_obj, "tobytes");
        PyObject* bytestr = PyObject_CallObject(tobytes_f, NULL);
        if (bytestr == NULL) {
            mpz_clear(in.i);
            Py_DECREF(tobytes_f);
            return NULL;
        }
        if (!PyString_Check(bytestr)) {
            PyErr_SetString(
                PyExc_ValueError,
                "The result of the object's tobytes() method must be a "
                "binary string.");
            mpz_clear(in.i);
            Py_DECREF(tobytes_f);
            Py_DECREF(bytestr);
            return NULL;
        }
        slack = PyString_Size(bytestr)*8 - PyObject_Size(in_obj);
#ifdef DEBUG
        printf("Length of byte string: %ld\n", PyString_Size(bytestr));
        printf("Length of object (bits): %ld\n", PyObject_Size(in_obj));
        printf("Expected trailing bits: %d (to be shifted out)\n", slack);
#endif
        if (PyString_Size(bytestr)*8 < PyObject_Size(in_obj) ||
            PyString_Size(bytestr) > (PyObject_Size(in_obj)/8 + 1))
        {
            PyErr_SetString(
                PyExc_TypeError,
                "The result of the object's len() method must be the number "
                "of bits in the string.");
            mpz_clear(in.i);
            Py_DECREF(tobytes_f);
            Py_DECREF(bytestr);
            return NULL;
        }

        mpz_import(in.i, //rop
                   PyString_Size(bytestr), //count
                   1, // order
                   1, // size
                   1, // endian
                   0, // nails
                   (void*)PyString_AsString(bytestr));
        mpz_tdiv_q_2exp(in.i, in.i, slack);
        in.len = PyObject_Size(in_obj);

        Py_DECREF(tobytes_f);
        Py_DECREF(bytestr);
    } else {
        PyErr_SetString(
            PyExc_TypeError,
            "A binary string or an object with both a tobytes() method and "
            "a len() method that returns the length in bits is required.");
        mpz_clear(in.i);
        return NULL;
    }

#ifdef DEBUG
    gmp_printf("The binary string: 0x%Zx, %d bits\n", in.i, in.len);
#endif

    if (in.len == 0) {
        PyErr_SetString(
            PyExc_ValueError,
            "The input string must have a non-zero length.");
        mpz_clear(in.i);
        return NULL;
    }

    retval = PyFloat_FromDouble(f(in));

    mpz_clear(in.i);

    return retval;
}

#define DOC_BIEN \
"bien(bits)\n" \
"\n" \
"BiEntropy, or BiEn for short, is a weighted average of the Shannon binary\n" \
"entropies of the string and the first n-2 binary derivatives of the string\n" \
"using a simple power law. This version of BiEntropy is suitable for\n" \
"shorter binary strings where n <= 32, approximately.\n" \
"\n" \
"This algorithm evaluates the order and disorder of a binary string of\n" \
"length n in O(n^2) time using O(n) memory.\n" \
"\n" \
"Parameters\n" \
"----------\n" \
"bits : bytes object or bitstring-like object\n" \
"    the input bitstring on which to operate; this function can accept a\n" \
"    Python bytes string or bitstring object (any object with a tobytes()\n" \
"    method that returns a byte string and a len() method that returns the\n" \
"    length in bits)\n" \
"\n" \
"Returns\n" \
"-------\n" \
"float\n" \
"    the BiEntropy of the input\n"
static PyObject *
bientropy_bien(PyObject *self, PyObject *args)
{
    return bientropy_wrapper(self, args, bien);
}

#define DOC_TBIEN \
"tbien(bits)\n" \
"\n" \
"The logarithmic weighting BiEntropy, or TBiEn for short, gives greater\n" \
"weight to the higher binary derivatives. As a result, has a slightly faster\n" \
"runtime because the weights tend to be smaller than for BiEn.\n" \
"\n" \
"This algorithm evaluates the order and disorder of a binary string of\n" \
"length n in O(n^2) time using O(n) memory.\n" \
"\n" \
"Parameters\n" \
"----------\n" \
"bits : bytes object or bitstring-like object\n" \
"    the input bitstring on which to operate; this function can accept a\n" \
"    Python bytes string or bitstring object (any object with a tobytes()\n" \
"    method that returns a byte string and a len() method that returns the\n" \
"    length in bits)\n" \
"\n" \
"Returns\n" \
"-------\n" \
"float\n" \
"    the TBiEntropy of the input\n"
static PyObject *
bientropy_tbien(PyObject *self, PyObject *args)
{
    return bientropy_wrapper(self, args, tbien);
}

static PyMethodDef BiEntropyMethods[] = {
    {"bien", bientropy_bien, METH_VARARGS, DOC_BIEN},
    {"tbien", bientropy_tbien, METH_VARARGS, DOC_TBIEN},
    {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3
static PyModuleDef BiEntropyModule = {
    PyModuleDef_HEAD_INIT,
    "cbientropy", // module name
    NULL, // doc string
    -1, // do not support sub-interpreters, use a global state
    BiEntropyMethods,
    NULL, // single-phase initialization
    NULL, // no GC traversal function
    NULL, // no GC clear function
    NULL, // no free function
};
#endif

PyMODINIT_FUNC
#if PY_MAJOR_VERSION >= 3
PyInit_cbientropy(void)
#else
initcbientropy(void)
#endif
{
    PyObject* m;

#if PY_MAJOR_VERSION >= 3
    m = PyModule_Create(&BiEntropyModule);
    if (m == NULL)
      return m;
#else
    (void) Py_InitModule("cbientropy", BiEntropyMethods);
    if (m == NULL)
      return;
#endif

#if PY_MAJOR_VERSION >= 3
    return m;
#endif
}
