/* widget_checkbox.c — Checkbox type. */
#include "module.h"

static int
Checkbox_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"text", NULL};
    const char *text;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &text))
        return -1;

    uiCheckbox *cb = uiNewCheckbox(text);
    if (cb == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewCheckbox failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(cb));
}

static PyObject *
Checkbox_get_text(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    char *t = uiCheckboxText(uiCheckbox(as_ctrl(self)->control));
    PyObject *s = PyUnicode_FromString(t);
    uiFreeText(t);
    return s;
}

static int
Checkbox_set_text(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    const char *t = PyUnicode_AsUTF8(value);
    if (t == NULL) return -1;
    uiCheckboxSetText(uiCheckbox(as_ctrl(self)->control), t);
    return 0;
}

static PyObject *
Checkbox_get_checked(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiCheckboxChecked(uiCheckbox(as_ctrl(self)->control)));
}

static int
Checkbox_set_checked(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiCheckboxSetChecked(uiCheckbox(as_ctrl(self)->control), PyObject_IsTrue(value));
    return 0;
}

static PyObject *
Checkbox_on_toggled(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_toggled", callable) < 0) return NULL;
    uiCheckboxOnToggled(uiCheckbox(c->control),
                        (void (*)(uiCheckbox *, void *))trampoline_void,
                        callable);
    Py_RETURN_NONE;
}

static PyMethodDef Checkbox_methods[] = {
    {"on_toggled", Checkbox_on_toggled, METH_VARARGS,
     "Register a callback for when the checkbox is toggled."},
    {NULL}
};

static PyGetSetDef Checkbox_getset[] = {
    {"text",    Checkbox_get_text,    Checkbox_set_text,
     "The checkbox label text.", NULL},
    {"checked", Checkbox_get_checked, Checkbox_set_checked,
     "Whether the checkbox is checked.", NULL},
    {NULL}
};

static PyType_Slot Checkbox_slots[] = {
    {Py_tp_init,      Checkbox_init},
    {Py_tp_methods,   Checkbox_methods},
    {Py_tp_getset,    Checkbox_getset},
    {Py_tp_doc,       "Checkbox(text)\n--\n\nA checkbox with a text label."},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Checkbox_spec = {
    .name      = "libui.core.Checkbox",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Checkbox_slots,
};
