/* widget_entry.c — Entry type. */
#include "module.h"

static int
Entry_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"type", NULL};
    const char *type = "normal";
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|s", kwlist, &type))
        return -1;

    uiEntry *e;
    if (strcmp(type, "password") == 0)
        e = uiNewPasswordEntry();
    else if (strcmp(type, "search") == 0)
        e = uiNewSearchEntry();
    else
        e = uiNewEntry();

    if (e == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewEntry failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(e));
}

static PyObject *
Entry_get_text(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    char *t = uiEntryText(uiEntry(as_ctrl(self)->control));
    PyObject *s = PyUnicode_FromString(t);
    uiFreeText(t);
    return s;
}

static int
Entry_set_text(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    const char *t = PyUnicode_AsUTF8(value);
    if (t == NULL) return -1;
    uiEntrySetText(uiEntry(as_ctrl(self)->control), t);
    return 0;
}

static PyObject *
Entry_get_read_only(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiEntryReadOnly(uiEntry(as_ctrl(self)->control)));
}

static int
Entry_set_read_only(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiEntrySetReadOnly(uiEntry(as_ctrl(self)->control), PyObject_IsTrue(value));
    return 0;
}

static PyObject *
Entry_on_changed(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_changed", callable) < 0) return NULL;
    uiEntryOnChanged(uiEntry(c->control),
                     (void (*)(uiEntry *, void *))trampoline_void,
                     callable);
    Py_RETURN_NONE;
}

static PyMethodDef Entry_methods[] = {
    {"on_changed", Entry_on_changed, METH_VARARGS,
     "Register a callback for when the text changes."},
    {NULL}
};

static PyGetSetDef Entry_getset[] = {
    {"text",      Entry_get_text,      Entry_set_text,
     "The entry text.", NULL},
    {"read_only", Entry_get_read_only, Entry_set_read_only,
     "Whether the entry is read-only.", NULL},
    {NULL}
};

static PyType_Slot Entry_slots[] = {
    {Py_tp_doc,       "Entry(type='normal')\n--\n\n"
                      "A single-line text entry. Type can be 'normal', "
                      "'password', or 'search'."},
    {Py_tp_init,      Entry_init},
    {Py_tp_methods,   Entry_methods},
    {Py_tp_getset,    Entry_getset},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Entry_spec = {
    .name      = "libui.core.Entry",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Entry_slots,
};
