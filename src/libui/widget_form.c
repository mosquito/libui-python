/* widget_form.c — Form type. */
#include "module.h"

static int
Form_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"padded", NULL};
    int padded = 1;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|p", kwlist, &padded))
        return -1;

    uiForm *f = uiNewForm();
    if (f == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewForm failed");
        return -1;
    }
    int rc = init_base(as_ctrl(self), uiControl(f));
    if (rc == 0 && padded)
        uiFormSetPadded(f, 1);
    return rc;
}

static PyObject *
Form_append(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"label", "child", "stretchy", NULL};
    const char *label;
    PyObject *child_obj;
    int stretchy = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "sO!|p", kwlist,
                                     &label, ControlType, &child_obj,
                                     &stretchy))
        return NULL;
    UiControlObject *self_c = as_ctrl(self);
    UiControlObject *child_c = as_ctrl(child_obj);
    if (check_control(self_c) < 0 || check_control(child_c) < 0)
        return NULL;

    uiFormAppend(uiForm(self_c->control), label, child_c->control, stretchy);
    child_c->owned = 0;
    PyList_Append(self_c->children, child_obj);
    Py_RETURN_NONE;
}

static PyObject *
Form_delete(PyObject *self, PyObject *args)
{
    int index;
    if (!PyArg_ParseTuple(args, "i", &index))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;

    Py_ssize_t n = PyList_Size(c->children);
    if (index < 0 || index >= n) {
        PyErr_SetString(PyExc_IndexError, "form child index out of range");
        return NULL;
    }

    uiFormDelete(uiForm(c->control), index);

    PyObject *child = PyList_GetItem(c->children, index);
    as_ctrl(child)->owned = 1;
    if (PyList_SetSlice(c->children, index, index + 1, NULL) < 0)
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
Form_get_padded(PyObject *self, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiFormPadded(uiForm(as_ctrl(self)->control)));
}

static int
Form_set_padded(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiFormSetPadded(uiForm(as_ctrl(self)->control), PyObject_IsTrue(value));
    return 0;
}

static PyMethodDef Form_methods[] = {
    {"append", (PyCFunction)Form_append, METH_VARARGS | METH_KEYWORDS,
     "append(label, child, *, stretchy=False)\n--\n\nAdd a labeled row."},
    {"delete", Form_delete,              METH_VARARGS,
     "delete(index)\n--\n\nRemove the row at index."},
    {NULL}
};

static PyGetSetDef Form_getset[] = {
    {"padded", Form_get_padded, Form_set_padded,
     "Whether the form has padding between rows.", NULL},
    {NULL}
};

static PyType_Slot Form_slots[] = {
    {Py_tp_doc,       "Form(padded=True)\n--\n\n"
                      "A two-column label-control form layout."},
    {Py_tp_init,      Form_init},
    {Py_tp_methods,   Form_methods},
    {Py_tp_getset,    Form_getset},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Form_spec = {
    .name      = "libui.core.Form",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Form_slots,
};
