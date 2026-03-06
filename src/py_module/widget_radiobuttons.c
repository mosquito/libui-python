/* widget_radiobuttons.c — RadioButtons type. */
#include "module.h"

static int
RadioButtons_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist))
        return -1;

    uiRadioButtons *r = uiNewRadioButtons();
    if (r == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewRadioButtons failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(r));
}

static PyObject *
RadioButtons_append(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    const char *text;
    if (!PyArg_ParseTuple(args, "s", &text))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    uiRadioButtonsAppend(uiRadioButtons(c->control), text);
    /* Track item count via children list (stores Python string markers) */
    PyObject *marker = PyUnicode_FromString(text);
    if (marker) { PyList_Append(c->children, marker); Py_DECREF(marker); }
    Py_RETURN_NONE;
}

static PyObject *
RadioButtons_get_selected(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyLong_FromLong(
        uiRadioButtonsSelected(uiRadioButtons(as_ctrl(self)->control)));
}

static int
RadioButtons_set_selected(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    UiControlObject *c = as_ctrl(self);
    int idx = (int)PyLong_AsLong(value);
    if (idx == -1 && PyErr_Occurred()) return -1;
    Py_ssize_t n = PyList_Size(c->children);
    if (idx < -1 || idx >= n) {
        PyErr_Format(PyExc_IndexError,
            "radio button index %d out of range (have %zd items)", idx, n);
        return -1;
    }
    uiRadioButtonsSetSelected(uiRadioButtons(c->control), idx);
    return 0;
}

static PyObject *
RadioButtons_on_selected(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_selected", callable) < 0) return NULL;
    uiRadioButtonsOnSelected(
        uiRadioButtons(c->control),
        (void (*)(uiRadioButtons *, void *))trampoline_void,
        callable);
    Py_RETURN_NONE;
}

static PyMethodDef RadioButtons_methods[] = {
    {"append",      RadioButtons_append,      METH_VARARGS,
     "append(text)\n--\n\nAdd a radio button."},
    {"on_selected", RadioButtons_on_selected, METH_VARARGS,
     "Register a callback for when the selection changes."},
    {NULL}
};

static PyGetSetDef RadioButtons_getset[] = {
    {"selected", RadioButtons_get_selected, RadioButtons_set_selected,
     "Index of the selected button, or -1.", NULL},
    {NULL}
};

static PyType_Slot RadioButtons_slots[] = {
    {Py_tp_init,      RadioButtons_init},
    {Py_tp_methods,   RadioButtons_methods},
    {Py_tp_getset,    RadioButtons_getset},
    {Py_tp_doc,       "RadioButtons()\n--\n\nA group of mutually exclusive radio buttons."},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec RadioButtons_spec = {
    .name      = "libui.core.RadioButtons",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = RadioButtons_slots,
};
