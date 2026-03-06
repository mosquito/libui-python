/* widget_combobox.c — Combobox type. */
#include "module.h"

static int
Combobox_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist))
        return -1;

    uiCombobox *cb = uiNewCombobox();
    if (cb == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewCombobox failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(cb));
}

static PyObject *
Combobox_append(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    const char *text;
    if (!PyArg_ParseTuple(args, "s", &text))
        return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiComboboxAppend(uiCombobox(as_ctrl(self)->control), text);
    Py_RETURN_NONE;
}

static PyObject *
Combobox_get_selected(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyLong_FromLong(uiComboboxSelected(uiCombobox(as_ctrl(self)->control)));
}

static int
Combobox_set_selected(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    int idx = (int)PyLong_AsLong(value);
    if (idx == -1 && PyErr_Occurred()) return -1;
    uiComboboxSetSelected(uiCombobox(as_ctrl(self)->control), idx);
    return 0;
}

static PyObject *
Combobox_on_selected(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_selected", callable) < 0) return NULL;
    uiComboboxOnSelected(uiCombobox(c->control),
                         (void (*)(uiCombobox *, void *))trampoline_void,
                         callable);
    Py_RETURN_NONE;
}

static PyMethodDef Combobox_methods[] = {
    {"append",      Combobox_append,      METH_VARARGS,
     "append(text)\n--\n\nAdd an item to the combobox."},
    {"on_selected", Combobox_on_selected, METH_VARARGS,
     "Register a callback for when the selection changes."},
    {NULL}
};

static PyGetSetDef Combobox_getset[] = {
    {"selected", Combobox_get_selected, Combobox_set_selected,
     "Index of the selected item, or -1.", NULL},
    {NULL}
};

static PyType_Slot Combobox_slots[] = {
    {Py_tp_init,      Combobox_init},
    {Py_tp_methods,   Combobox_methods},
    {Py_tp_getset,    Combobox_getset},
    {Py_tp_doc,       "Combobox()\n--\n\nA drop-down selection control."},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Combobox_spec = {
    .name      = "libui.core.Combobox",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Combobox_slots,
};
