/* widget_spinbox.c — Spinbox type. */
#include "module.h"

static int
Spinbox_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"min", "max", NULL};
    int min = 0, max = 100;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|ii", kwlist, &min, &max))
        return -1;

    uiSpinbox *s = uiNewSpinbox(min, max);
    if (s == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewSpinbox failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(s));
}

static PyObject *
Spinbox_get_value(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyLong_FromLong(uiSpinboxValue(uiSpinbox(as_ctrl(self)->control)));
}

static int
Spinbox_set_value(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    int v = (int)PyLong_AsLong(value);
    if (v == -1 && PyErr_Occurred()) return -1;
    uiSpinboxSetValue(uiSpinbox(as_ctrl(self)->control), v);
    return 0;
}

static PyObject *
Spinbox_on_changed(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_changed", callable) < 0) return NULL;
    uiSpinboxOnChanged(uiSpinbox(c->control),
                       (void (*)(uiSpinbox *, void *))trampoline_void,
                       callable);
    Py_RETURN_NONE;
}

static PyMethodDef Spinbox_methods[] = {
    {"on_changed", Spinbox_on_changed, METH_VARARGS,
     "Register a callback for when the value changes."},
    {NULL}
};

static PyGetSetDef Spinbox_getset[] = {
    {"value", Spinbox_get_value, Spinbox_set_value,
     "The current integer value.", NULL},
    {NULL}
};

static PyType_Slot Spinbox_slots[] = {
    {Py_tp_init,      Spinbox_init},
    {Py_tp_methods,   Spinbox_methods},
    {Py_tp_getset,    Spinbox_getset},
    {Py_tp_doc,       "Spinbox(min=0, max=100)\n--\n\nA numeric input with up/down buttons."},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Spinbox_spec = {
    .name      = "libui.core.Spinbox",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Spinbox_slots,
};
