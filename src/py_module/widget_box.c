/*
 * _core_box.c — Box, VerticalBox, HorizontalBox types.
 */
#include "module.h"

/* -- Box ----------------------------------------------------------- */

static int
Box_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"vertical", "padded", NULL};
    int vertical = 1, padded = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|pp", kwlist,
                                     &vertical, &padded))
        return -1;

    uiBox *b = vertical ? uiNewVerticalBox() : uiNewHorizontalBox();
    if (b == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewBox failed");
        return -1;
    }
    int rc = init_base(as_ctrl(self), uiControl(b));
    if (rc == 0 && padded)
        uiBoxSetPadded(b, 1);
    return rc;
}

static PyObject *
Box_append(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD;
    static char *kwlist[] = {"child", "stretchy", NULL};
    PyObject *child_obj;
    int stretchy = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|p", kwlist,
                                     ControlType, &child_obj, &stretchy))
        return NULL;
    UiControlObject *self_c = as_ctrl(self);
    UiControlObject *child_c = as_ctrl(child_obj);
    if (check_control(self_c) < 0 || check_control(child_c) < 0
        || check_no_parent(child_c) < 0)
        return NULL;

    uiBoxAppend(uiBox(self_c->control), child_c->control, stretchy);
    child_c->owned = 0;
    PyList_Append(self_c->children, child_obj);
    Py_RETURN_NONE;
}

static PyObject *
Box_delete(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    int index;
    if (!PyArg_ParseTuple(args, "i", &index))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;

    Py_ssize_t n = PyList_Size(c->children);
    if (index < 0 || index >= n) {
        PyErr_SetString(PyExc_IndexError, "box child index out of range");
        return NULL;
    }

    uiBoxDelete(uiBox(c->control), index);

    PyObject *child = PyList_GetItem(c->children, index);
    as_ctrl(child)->owned = 1;
    if (PyList_SetSlice(c->children, index, index + 1, NULL) < 0)
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
Box_get_padded(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiBoxPadded(uiBox(as_ctrl(self)->control)));
}

static int
Box_set_padded(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiBoxSetPadded(uiBox(as_ctrl(self)->control), PyObject_IsTrue(value));
    return 0;
}

static PyMethodDef Box_methods[] = {
    {"append", (PyCFunction)Box_append, METH_VARARGS | METH_KEYWORDS,
     "append(child, *, stretchy=False)\n--\n\nAdd a child control."},
    {"delete", Box_delete,              METH_VARARGS,
     "delete(index)\n--\n\nRemove the child at index."},
    {NULL}
};

static PyGetSetDef Box_getset[] = {
    {"padded", Box_get_padded, Box_set_padded,
     "Whether the box has padding between children.", NULL},
    {NULL}
};

static PyType_Slot Box_slots[] = {
    {Py_tp_doc,       "Box(vertical=True, padded=False)\n--\n\n"
                      "A container that stacks children."},
    {Py_tp_init,      Box_init},
    {Py_tp_methods,   Box_methods},
    {Py_tp_getset,    Box_getset},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Box_spec = {
    .name      = "libui.core.Box",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Box_slots,
};

/* -- VerticalBox --------------------------------------------------- */

static int
VerticalBox_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"padded", NULL};
    int padded = 1;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|p", kwlist, &padded))
        return -1;

    uiBox *b = uiNewVerticalBox();
    if (b == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewVerticalBox failed");
        return -1;
    }
    int rc = init_base(as_ctrl(self), uiControl(b));
    if (rc == 0 && padded)
        uiBoxSetPadded(b, 1);
    return rc;
}

static PyType_Slot VerticalBox_slots[] = {
    {Py_tp_doc,       "VerticalBox(padded=True)\n--\n\n"
                      "A vertical box container."},
    {Py_tp_init,      VerticalBox_init},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec VerticalBox_spec = {
    .name      = "libui.core.VerticalBox",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = VerticalBox_slots,
};

/* -- HorizontalBox ------------------------------------------------- */

static int
HorizontalBox_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"padded", NULL};
    int padded = 1;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|p", kwlist, &padded))
        return -1;

    uiBox *b = uiNewHorizontalBox();
    if (b == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewHorizontalBox failed");
        return -1;
    }
    int rc = init_base(as_ctrl(self), uiControl(b));
    if (rc == 0 && padded)
        uiBoxSetPadded(b, 1);
    return rc;
}

static PyType_Slot HorizontalBox_slots[] = {
    {Py_tp_doc,       "HorizontalBox(padded=True)\n--\n\n"
                      "A horizontal box container."},
    {Py_tp_init,      HorizontalBox_init},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec HorizontalBox_spec = {
    .name      = "libui.core.HorizontalBox",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = HorizontalBox_slots,
};
