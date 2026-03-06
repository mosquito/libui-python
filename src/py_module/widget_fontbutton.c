/* widget_fontbutton.c — FontButton type. */
#include "module.h"

static int
FontButton_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist))
        return -1;

    uiFontButton *b = uiNewFontButton();
    if (b == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewFontButton failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(b));
}

static PyObject *
FontButton_get_font(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;

    uiFontDescriptor desc;
    uiFontButtonFont(uiFontButton(as_ctrl(self)->control), &desc);

    PyObject *d = Py_BuildValue(
        "{s:s, s:d, s:i, s:i, s:i}",
        "family", desc.Family,
        "size",   desc.Size,
        "weight", (int)desc.Weight,
        "italic", (int)desc.Italic,
        "stretch", (int)desc.Stretch);

    uiFreeFontButtonFont(&desc);
    return d;
}

static PyObject *
FontButton_on_changed(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_changed", callable) < 0) return NULL;
    uiFontButtonOnChanged(
        uiFontButton(c->control),
        (void (*)(uiFontButton *, void *))trampoline_void,
        callable);
    Py_RETURN_NONE;
}

static PyMethodDef FontButton_methods[] = {
    {"on_changed", FontButton_on_changed, METH_VARARGS,
     "Register a callback for when the font changes."},
    {NULL}
};

static PyGetSetDef FontButton_getset[] = {
    {"font", FontButton_get_font, NULL,
     "The selected font as a dict with 'family', 'size', 'weight', 'italic', 'stretch'.",
     NULL},
    {NULL}
};

static PyType_Slot FontButton_slots[] = {
    {Py_tp_init,      FontButton_init},
    {Py_tp_methods,   FontButton_methods},
    {Py_tp_getset,    FontButton_getset},
    {Py_tp_doc,       "FontButton()\n--\n\n"
                      "A button that opens a font picker."},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec FontButton_spec = {
    .name      = "libui.core.FontButton",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = FontButton_slots,
};
