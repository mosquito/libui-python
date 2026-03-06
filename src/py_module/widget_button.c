/* widget_button.c — Button type. */
#include "module.h"

static int
Button_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"text", NULL};
    const char *text;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &text))
        return -1;

    uiButton *b = uiNewButton(text);
    if (b == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewButton failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(b));
}

static PyObject *
Button_get_text(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    char *t = uiButtonText(uiButton(as_ctrl(self)->control));
    PyObject *s = PyUnicode_FromString(t);
    uiFreeText(t);
    return s;
}

static int
Button_set_text(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    const char *t = PyUnicode_AsUTF8(value);
    if (t == NULL) return -1;
    uiButtonSetText(uiButton(as_ctrl(self)->control), t);
    return 0;
}

static PyObject *
Button_on_clicked(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_clicked", callable) < 0) return NULL;
    uiButtonOnClicked(uiButton(c->control),
                      (void (*)(uiButton *, void *))trampoline_void,
                      callable);
    Py_RETURN_NONE;
}

static PyMethodDef Button_methods[] = {
    {"on_clicked", Button_on_clicked, METH_VARARGS,
     "Register a callback for when the button is clicked."},
    {NULL}
};

static PyGetSetDef Button_getset[] = {
    {"text", Button_get_text, Button_set_text, "The button label text.", NULL},
    {NULL}
};

static PyType_Slot Button_slots[] = {
    {Py_tp_doc,       "Button(text)\n--\n\nA clickable button."},
    {Py_tp_init,      Button_init},
    {Py_tp_methods,   Button_methods},
    {Py_tp_getset,    Button_getset},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Button_spec = {
    .name      = "libui.core.Button",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Button_slots,
};
