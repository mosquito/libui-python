/* widget_progressbar.c — ProgressBar type. */
#include "module.h"

static int
ProgressBar_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist))
        return -1;

    uiProgressBar *p = uiNewProgressBar();
    if (p == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewProgressBar failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(p));
}

static PyObject *
ProgressBar_get_value(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyLong_FromLong(uiProgressBarValue(uiProgressBar(as_ctrl(self)->control)));
}

static int
ProgressBar_set_value(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    int v = (int)PyLong_AsLong(value);
    if (v == -1 && PyErr_Occurred()) return -1;
    if (v < -1 || v > 100) {
        PyErr_SetString(PyExc_ValueError,
            "progress bar value must be -1 (indeterminate) or 0-100");
        return -1;
    }
    uiProgressBarSetValue(uiProgressBar(as_ctrl(self)->control), v);
    return 0;
}

static PyGetSetDef ProgressBar_getset[] = {
    {"value", ProgressBar_get_value, ProgressBar_set_value,
     "The current value (0-100), or -1 for indeterminate.", NULL},
    {NULL}
};

static PyType_Slot ProgressBar_slots[] = {
    {Py_tp_init,      ProgressBar_init},
    {Py_tp_getset,    ProgressBar_getset},
    {Py_tp_doc,       "ProgressBar()\n--\n\nA progress bar. Set value 0-100, or -1 for indeterminate."},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec ProgressBar_spec = {
    .name      = "libui.core.ProgressBar",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = ProgressBar_slots,
};
