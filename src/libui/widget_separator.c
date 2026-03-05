/* widget_separator.c — Separator type. */
#include "module.h"

static int
Separator_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"vertical", NULL};
    int vertical = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|p", kwlist, &vertical))
        return -1;

    uiSeparator *s = vertical
        ? uiNewVerticalSeparator()
        : uiNewHorizontalSeparator();
    if (s == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewSeparator failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(s));
}

static PyType_Slot Separator_slots[] = {
    {Py_tp_init,      Separator_init},
    {Py_tp_doc,       "Separator(vertical=False)\n--\n\nA visual separator line."},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Separator_spec = {
    .name      = "libui.core.Separator",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Separator_slots,
};
