/* widget_multilineentry.c — MultilineEntry type. */
#include "module.h"

static int
MultilineEntry_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"wrapping", NULL};
    int wrapping = 1;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|p", kwlist, &wrapping))
        return -1;

    uiMultilineEntry *e = wrapping
        ? uiNewMultilineEntry()
        : uiNewNonWrappingMultilineEntry();
    if (e == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewMultilineEntry failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(e));
}

static PyObject *
MultilineEntry_get_text(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    char *t = uiMultilineEntryText(
        uiMultilineEntry(as_ctrl(self)->control));
    PyObject *s = PyUnicode_FromString(t);
    uiFreeText(t);
    return s;
}

static int
MultilineEntry_set_text(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    const char *t = PyUnicode_AsUTF8(value);
    if (t == NULL) return -1;
    uiMultilineEntrySetText(
        uiMultilineEntry(as_ctrl(self)->control), t);
    return 0;
}

static PyObject *
MultilineEntry_append(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    const char *text;
    if (!PyArg_ParseTuple(args, "s", &text))
        return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiMultilineEntryAppend(
        uiMultilineEntry(as_ctrl(self)->control), text);
    Py_RETURN_NONE;
}

static PyObject *
MultilineEntry_get_read_only(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(
        uiMultilineEntryReadOnly(uiMultilineEntry(as_ctrl(self)->control)));
}

static int
MultilineEntry_set_read_only(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiMultilineEntrySetReadOnly(
        uiMultilineEntry(as_ctrl(self)->control), PyObject_IsTrue(value));
    return 0;
}

static PyObject *
MultilineEntry_on_changed(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_changed", callable) < 0) return NULL;
    uiMultilineEntryOnChanged(
        uiMultilineEntry(c->control),
        (void (*)(uiMultilineEntry *, void *))trampoline_void,
        callable);
    Py_RETURN_NONE;
}

static PyMethodDef MultilineEntry_methods[] = {
    {"append",     MultilineEntry_append,     METH_VARARGS,
     "append(text)\n--\n\nAppend text to the entry."},
    {"on_changed", MultilineEntry_on_changed, METH_VARARGS,
     "Register a callback for when the text changes."},
    {NULL}
};

static PyGetSetDef MultilineEntry_getset[] = {
    {"text",      MultilineEntry_get_text,      MultilineEntry_set_text,
     "The entry text.", NULL},
    {"read_only", MultilineEntry_get_read_only, MultilineEntry_set_read_only,
     "Whether the entry is read-only.", NULL},
    {NULL}
};

static PyType_Slot MultilineEntry_slots[] = {
    {Py_tp_init,      MultilineEntry_init},
    {Py_tp_methods,   MultilineEntry_methods},
    {Py_tp_getset,    MultilineEntry_getset},
    {Py_tp_doc,       "MultilineEntry(wrapping=True)\n--\n\n"
                      "A multi-line text entry."},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec MultilineEntry_spec = {
    .name      = "libui.core.MultilineEntry",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = MultilineEntry_slots,
};
