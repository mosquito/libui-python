/* widget_slider.c — Slider type. */
#include "module.h"

static int
Slider_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"min", "max", NULL};
    int min = 0, max = 100;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|ii", kwlist, &min, &max))
        return -1;

    uiSlider *s = uiNewSlider(min, max);
    if (s == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewSlider failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(s));
}

static PyObject *
Slider_get_value(PyObject *self, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyLong_FromLong(uiSliderValue(uiSlider(as_ctrl(self)->control)));
}

static int
Slider_set_value(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    int v = (int)PyLong_AsLong(value);
    if (v == -1 && PyErr_Occurred()) return -1;
    uiSliderSetValue(uiSlider(as_ctrl(self)->control), v);
    return 0;
}

static PyObject *
Slider_get_has_tooltip(PyObject *self, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiSliderHasToolTip(uiSlider(as_ctrl(self)->control)));
}

static int
Slider_set_has_tooltip(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiSliderSetHasToolTip(uiSlider(as_ctrl(self)->control), PyObject_IsTrue(value));
    return 0;
}

static PyObject *
Slider_set_range(PyObject *self, PyObject *args)
{
    int min, max;
    if (!PyArg_ParseTuple(args, "ii", &min, &max))
        return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiSliderSetRange(uiSlider(as_ctrl(self)->control), min, max);
    Py_RETURN_NONE;
}

static PyObject *
Slider_on_changed(PyObject *self, PyObject *args)
{
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_changed", callable) < 0) return NULL;
    uiSliderOnChanged(uiSlider(c->control),
                      (void (*)(uiSlider *, void *))trampoline_void,
                      callable);
    Py_RETURN_NONE;
}

static PyObject *
Slider_on_released(PyObject *self, PyObject *args)
{
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_released", callable) < 0) return NULL;
    uiSliderOnReleased(uiSlider(c->control),
                       (void (*)(uiSlider *, void *))trampoline_void,
                       callable);
    Py_RETURN_NONE;
}

static PyMethodDef Slider_methods[] = {
    {"set_range",   Slider_set_range,   METH_VARARGS,
     "set_range(min, max)\n--\n\nChange the slider range."},
    {"on_changed",  Slider_on_changed,  METH_VARARGS,
     "Register a callback for when the value changes."},
    {"on_released", Slider_on_released, METH_VARARGS,
     "Register a callback for when the slider is released."},
    {NULL}
};

static PyGetSetDef Slider_getset[] = {
    {"value",       Slider_get_value,       Slider_set_value,
     "The current integer value.", NULL},
    {"has_tooltip", Slider_get_has_tooltip, Slider_set_has_tooltip,
     "Whether the slider shows a tooltip.", NULL},
    {NULL}
};

static PyType_Slot Slider_slots[] = {
    {Py_tp_init,      Slider_init},
    {Py_tp_methods,   Slider_methods},
    {Py_tp_getset,    Slider_getset},
    {Py_tp_doc,       "Slider(min=0, max=100)\n--\n\nA horizontal slider control."},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Slider_spec = {
    .name      = "libui.core.Slider",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Slider_slots,
};
