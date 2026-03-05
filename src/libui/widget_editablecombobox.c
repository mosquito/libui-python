/* widget_editablecombobox.c — EditableCombobox type. */
#include "module.h"

static int
EditableCombobox_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist))
        return -1;

    uiEditableCombobox *c = uiNewEditableCombobox();
    if (c == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewEditableCombobox failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(c));
}

static PyObject *
EditableCombobox_append(PyObject *self, PyObject *args)
{
    const char *text;
    if (!PyArg_ParseTuple(args, "s", &text))
        return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiEditableComboboxAppend(uiEditableCombobox(as_ctrl(self)->control), text);
    Py_RETURN_NONE;
}

static PyObject *
EditableCombobox_get_text(PyObject *self, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    char *t = uiEditableComboboxText(uiEditableCombobox(as_ctrl(self)->control));
    PyObject *s = PyUnicode_FromString(t);
    uiFreeText(t);
    return s;
}

static int
EditableCombobox_set_text(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    const char *t = PyUnicode_AsUTF8(value);
    if (t == NULL) return -1;
    uiEditableComboboxSetText(uiEditableCombobox(as_ctrl(self)->control), t);
    return 0;
}

static PyObject *
EditableCombobox_on_changed(PyObject *self, PyObject *args)
{
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_changed", callable) < 0) return NULL;
    uiEditableComboboxOnChanged(
        uiEditableCombobox(c->control),
        (void (*)(uiEditableCombobox *, void *))trampoline_void,
        callable);
    Py_RETURN_NONE;
}

static PyMethodDef EditableCombobox_methods[] = {
    {"append",     EditableCombobox_append,     METH_VARARGS,
     "append(text)\n--\n\nAdd an item."},
    {"on_changed", EditableCombobox_on_changed, METH_VARARGS,
     "Register a callback for when the text changes."},
    {NULL}
};

static PyGetSetDef EditableCombobox_getset[] = {
    {"text", EditableCombobox_get_text, EditableCombobox_set_text,
     "The current text.", NULL},
    {NULL}
};

static PyType_Slot EditableCombobox_slots[] = {
    {Py_tp_init,      EditableCombobox_init},
    {Py_tp_methods,   EditableCombobox_methods},
    {Py_tp_getset,    EditableCombobox_getset},
    {Py_tp_doc,       "EditableCombobox()\n--\n\nA combobox that also allows free-text input."},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec EditableCombobox_spec = {
    .name      = "libui.core.EditableCombobox",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = EditableCombobox_slots,
};
