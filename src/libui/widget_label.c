/* widget_label.c — Label type. */
#include "module.h"

static int
Label_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"text", NULL};
    const char *text;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &text))
        return -1;

    uiLabel *l = uiNewLabel(text);
    if (l == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewLabel failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(l));
}

static PyObject *
Label_get_text(PyObject *self, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    char *t = uiLabelText(uiLabel(as_ctrl(self)->control));
    PyObject *s = PyUnicode_FromString(t);
    uiFreeText(t);
    return s;
}

static int
Label_set_text(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    const char *t = PyUnicode_AsUTF8(value);
    if (t == NULL) return -1;
    uiLabelSetText(uiLabel(as_ctrl(self)->control), t);
    return 0;
}

static PyGetSetDef Label_getset[] = {
    {"text", Label_get_text, Label_set_text, "The label text.", NULL},
    {NULL}
};

static PyType_Slot Label_slots[] = {
    {Py_tp_doc,       "Label(text)\n--\n\nA static text label."},
    {Py_tp_init,      Label_init},
    {Py_tp_getset,    Label_getset},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Label_spec = {
    .name      = "libui.core.Label",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Label_slots,
};
