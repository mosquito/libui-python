/* widget_tab.c — Tab type. */
#include "module.h"

static int
Tab_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist))
        return -1;

    uiTab *t = uiNewTab();
    if (t == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewTab failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(t));
}

static PyObject *
Tab_append(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    const char *name;
    PyObject *child_obj;
    if (!PyArg_ParseTuple(args, "sO!", &name, ControlType, &child_obj))
        return NULL;
    UiControlObject *self_c = as_ctrl(self);
    UiControlObject *child_c = as_ctrl(child_obj);
    if (check_control(self_c) < 0 || check_control(child_c) < 0)
        return NULL;

    uiTabAppend(uiTab(self_c->control), name, child_c->control);
    child_c->owned = 0;
    PyList_Append(self_c->children, child_obj);
    Py_RETURN_NONE;
}

static PyObject *
Tab_insert_at(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    const char *name;
    int index;
    PyObject *child_obj;
    if (!PyArg_ParseTuple(args, "siO!", &name, &index, ControlType, &child_obj))
        return NULL;
    UiControlObject *self_c = as_ctrl(self);
    UiControlObject *child_c = as_ctrl(child_obj);
    if (check_control(self_c) < 0 || check_control(child_c) < 0)
        return NULL;

    uiTabInsertAt(uiTab(self_c->control), name, index, child_c->control);
    child_c->owned = 0;
    if (PyList_Insert(self_c->children, index, child_obj) < 0)
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
Tab_delete(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    int index;
    if (!PyArg_ParseTuple(args, "i", &index))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;

    Py_ssize_t n = PyList_Size(c->children);
    if (index < 0 || index >= n) {
        PyErr_SetString(PyExc_IndexError, "tab page index out of range");
        return NULL;
    }

    uiTabDelete(uiTab(c->control), index);

    PyObject *child = PyList_GetItem(c->children, index);
    as_ctrl(child)->owned = 1;
    if (PyList_SetSlice(c->children, index, index + 1, NULL) < 0)
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
Tab_num_pages(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyLong_FromLong(uiTabNumPages(uiTab(as_ctrl(self)->control)));
}

static PyObject *
Tab_margined(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    int index;
    if (!PyArg_ParseTuple(args, "i", &index))
        return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiTabMargined(uiTab(as_ctrl(self)->control), index));
}

static PyObject *
Tab_set_margined(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    int index, margined;
    if (!PyArg_ParseTuple(args, "ip", &index, &margined))
        return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiTabSetMargined(uiTab(as_ctrl(self)->control), index, margined);
    Py_RETURN_NONE;
}

static PyObject *
Tab_get_selected(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyLong_FromLong(uiTabSelected(uiTab(as_ctrl(self)->control)));
}

static int
Tab_set_selected(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    int idx = (int)PyLong_AsLong(value);
    if (idx == -1 && PyErr_Occurred()) return -1;
    uiTabSetSelected(uiTab(as_ctrl(self)->control), idx);
    return 0;
}

static PyObject *
Tab_on_selected(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_selected", callable) < 0) return NULL;
    uiTabOnSelected(uiTab(c->control),
                    (void (*)(uiTab *, void *))trampoline_void,
                    callable);
    Py_RETURN_NONE;
}

static PyMethodDef Tab_methods[] = {
    {"append",       Tab_append,       METH_VARARGS,
     "append(name, child)\n--\n\nAdd a tab page."},
    {"insert_at",    Tab_insert_at,    METH_VARARGS,
     "insert_at(name, index, child)\n--\n\nInsert a tab page at index."},
    {"delete",       Tab_delete,       METH_VARARGS,
     "delete(index)\n--\n\nRemove the tab page at index."},
    {"num_pages",    Tab_num_pages,    METH_NOARGS,
     "Return the number of tab pages."},
    {"margined",     Tab_margined,     METH_VARARGS,
     "margined(index)\n--\n\nReturn whether the page at index has a margin."},
    {"set_margined", Tab_set_margined, METH_VARARGS,
     "set_margined(index, margined)\n--\n\nSet margin for the page at index."},
    {"on_selected",  Tab_on_selected,  METH_VARARGS,
     "Register a callback for when the selected tab changes."},
    {NULL}
};

static PyGetSetDef Tab_getset[] = {
    {"selected", Tab_get_selected, Tab_set_selected,
     "Index of the selected tab.", NULL},
    {NULL}
};

static PyType_Slot Tab_slots[] = {
    {Py_tp_doc,       "Tab()\n--\n\nA tabbed container."},
    {Py_tp_init,      Tab_init},
    {Py_tp_methods,   Tab_methods},
    {Py_tp_getset,    Tab_getset},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Tab_spec = {
    .name      = "libui.core.Tab",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Tab_slots,
};
