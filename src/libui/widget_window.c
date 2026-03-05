/*
 * _core_window.c — Window type.
 */
#include "module.h"

static int
Window_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {
        "title", "width", "height", "has_menubar", "margined", NULL,
    };
    const char *title;
    int width = 640, height = 480, has_menubar = 0, margined = 1;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|iipp", kwlist,
                                     &title, &width, &height,
                                     &has_menubar, &margined))
        return -1;

    uiWindow *w = uiNewWindow(title, width, height, has_menubar);
    if (w == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewWindow failed");
        return -1;
    }

    int rc = init_base(as_ctrl(self), uiControl(w));
    if (rc == 0 && margined)
        uiWindowSetMargined(w, 1);
    return rc;
}

/* -- title --------------------------------------------------------- */

static PyObject *
Window_get_title(PyObject *self, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    char *t = uiWindowTitle(uiWindow(as_ctrl(self)->control));
    PyObject *s = PyUnicode_FromString(t);
    uiFreeText(t);
    return s;
}

static int
Window_set_title(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    const char *t = PyUnicode_AsUTF8(value);
    if (t == NULL) return -1;
    uiWindowSetTitle(uiWindow(as_ctrl(self)->control), t);
    return 0;
}

/* -- margined ------------------------------------------------------ */

static PyObject *
Window_get_margined(PyObject *self, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiWindowMargined(uiWindow(as_ctrl(self)->control)));
}

static int
Window_set_margined(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiWindowSetMargined(uiWindow(as_ctrl(self)->control), PyObject_IsTrue(value));
    return 0;
}

/* -- fullscreen ---------------------------------------------------- */

static PyObject *
Window_get_fullscreen(PyObject *self, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiWindowFullscreen(uiWindow(as_ctrl(self)->control)));
}

static int
Window_set_fullscreen(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiWindowSetFullscreen(uiWindow(as_ctrl(self)->control), PyObject_IsTrue(value));
    return 0;
}

/* -- borderless ---------------------------------------------------- */

static PyObject *
Window_get_borderless(PyObject *self, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiWindowBorderless(uiWindow(as_ctrl(self)->control)));
}

static int
Window_set_borderless(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiWindowSetBorderless(uiWindow(as_ctrl(self)->control), PyObject_IsTrue(value));
    return 0;
}

/* -- resizeable ---------------------------------------------------- */

static PyObject *
Window_get_resizeable(PyObject *self, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiWindowResizeable(uiWindow(as_ctrl(self)->control)));
}

static int
Window_set_resizeable(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiWindowSetResizeable(uiWindow(as_ctrl(self)->control), PyObject_IsTrue(value));
    return 0;
}

/* -- set_child ----------------------------------------------------- */

static PyObject *
Window_set_child(PyObject *self, PyObject *args)
{
    PyObject *child_obj;
    if (!PyArg_ParseTuple(args, "O!", ControlType, &child_obj))
        return NULL;
    UiControlObject *self_c = as_ctrl(self);
    UiControlObject *child_c = as_ctrl(child_obj);
    if (check_control(self_c) < 0 || check_control(child_c) < 0)
        return NULL;

    uiWindowSetChild(uiWindow(self_c->control), child_c->control);
    child_c->owned = 0;
    PyList_Append(self_c->children, child_obj);
    Py_RETURN_NONE;
}

/* -- on_closing ---------------------------------------------------- */

/*
 * Special trampoline for on_closing: if the user's callback returns True,
 * libui will destroy the window and all its children. We must invalidate
 * the Python-side control pointers so dealloc doesn't double-free.
 * We pass the Python Window object (self) as data, not the callable.
 */
static int
window_closing_trampoline(uiWindow *sender, void *data)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    UiControlObject *win = (UiControlObject *)data;

    /* Look up the callback from the window's dict */
    PyObject *key = PyUnicode_InternFromString("on_closing");
    PyObject *callable = PyDict_GetItemWithError(win->callbacks, key);
    Py_DECREF(key);

    int ret = 0;
    if (callable == NULL) {
        if (PyErr_Occurred())
            PyErr_WriteUnraisable((PyObject *)win);
    } else {
        PyObject *result = PyObject_CallNoArgs(callable);
        if (result == NULL) {
            PyErr_WriteUnraisable(callable);
        } else if (PyCoro_CheckExact(result)) {
            /* async callback — schedule on asyncio thread, don't destroy */
            schedule_coroutine_threadsafe(result, callable);
            Py_DECREF(result);
        } else {
            ret = PyObject_IsTrue(result);
            Py_DECREF(result);
        }
    }

    if (ret) {
        /* libui will destroy the window and all children — invalidate them */
        invalidate_control_tree(win);
    }

    PyGILState_Release(gstate);
    return ret;
}

static PyObject *
Window_on_closing(PyObject *self, PyObject *args)
{
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_closing", callable) < 0) return NULL;

    /* Pass 'self' as data so the trampoline can invalidate the tree */
    uiWindowOnClosing(uiWindow(c->control),
                      window_closing_trampoline,
                      (void *)c);
    Py_RETURN_NONE;
}

/* -- Type definition ----------------------------------------------- */

static PyMethodDef Window_methods[] = {
    {"set_child",  Window_set_child,  METH_VARARGS,
     "Set the window's child control."},
    {"on_closing", Window_on_closing, METH_VARARGS,
     "Register a callback for when the window is closing.\n\n"
     "Return True to allow the close, False to prevent it."},
    {NULL}
};

static PyGetSetDef Window_getset[] = {
    {"title",      Window_get_title,      Window_set_title,
     "The window title.", NULL},
    {"margined",   Window_get_margined,   Window_set_margined,
     "Whether the window has a margin.", NULL},
    {"fullscreen", Window_get_fullscreen, Window_set_fullscreen,
     "Whether the window is fullscreen.", NULL},
    {"borderless", Window_get_borderless, Window_set_borderless,
     "Whether the window is borderless.", NULL},
    {"resizeable", Window_get_resizeable, Window_set_resizeable,
     "Whether the window is resizeable.", NULL},
    {NULL}
};

static PyType_Slot Window_slots[] = {
    {Py_tp_doc,       "Window(title, width=640, height=480, *, has_menubar=False, margined=True)\n--\n\nA top-level window."},
    {Py_tp_init,      Window_init},
    {Py_tp_methods,   Window_methods},
    {Py_tp_getset,    Window_getset},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Window_spec = {
    .name      = "libui.core.Window",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Window_slots,
};
