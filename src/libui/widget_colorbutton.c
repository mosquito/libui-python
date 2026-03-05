/* widget_colorbutton.c — ColorButton type. */
#include "module.h"

static int
ColorButton_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist))
        return -1;

    uiColorButton *b = uiNewColorButton();
    if (b == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewColorButton failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(b));
}

static PyObject *
ColorButton_get_color(PyObject *self, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    double r, g, b, a;
    uiColorButtonColor(
        uiColorButton(as_ctrl(self)->control), &r, &g, &b, &a);
    return Py_BuildValue("(dddd)", r, g, b, a);
}

static int
ColorButton_set_color(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    PyObject *seq = PySequence_Fast(value, "color must be (r, g, b, a)");
    if (seq == NULL) return -1;
    if (PySequence_Fast_GET_SIZE(seq) != 4) {
        Py_DECREF(seq);
        PyErr_SetString(PyExc_ValueError,
                        "color must be a (r, g, b, a) tuple");
        return -1;
    }
    double r = PyFloat_AsDouble(PySequence_Fast_GET_ITEM(seq, 0));
    double g = PyFloat_AsDouble(PySequence_Fast_GET_ITEM(seq, 1));
    double b = PyFloat_AsDouble(PySequence_Fast_GET_ITEM(seq, 2));
    double a = PyFloat_AsDouble(PySequence_Fast_GET_ITEM(seq, 3));
    Py_DECREF(seq);
    if (PyErr_Occurred()) return -1;
    uiColorButtonSetColor(
        uiColorButton(as_ctrl(self)->control), r, g, b, a);
    return 0;
}

static PyObject *
ColorButton_on_changed(PyObject *self, PyObject *args)
{
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_changed", callable) < 0) return NULL;
    uiColorButtonOnChanged(
        uiColorButton(c->control),
        (void (*)(uiColorButton *, void *))trampoline_void,
        callable);
    Py_RETURN_NONE;
}

static PyMethodDef ColorButton_methods[] = {
    {"on_changed", ColorButton_on_changed, METH_VARARGS,
     "Register a callback for when the color changes."},
    {NULL}
};

static PyGetSetDef ColorButton_getset[] = {
    {"color", ColorButton_get_color, ColorButton_set_color,
     "The selected color as an (r, g, b, a) tuple of floats.", NULL},
    {NULL}
};

static PyType_Slot ColorButton_slots[] = {
    {Py_tp_init,      ColorButton_init},
    {Py_tp_methods,   ColorButton_methods},
    {Py_tp_getset,    ColorButton_getset},
    {Py_tp_doc,       "ColorButton()\n--\n\n"
                      "A button that opens a color picker."},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec ColorButton_spec = {
    .name      = "libui.core.ColorButton",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = ColorButton_slots,
};
