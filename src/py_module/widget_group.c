/* widget_group.c — Group type. */
#include "module.h"

static int
Group_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"title", "margined", NULL};
    const char *title;
    int margined = 1;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|p", kwlist,
                                     &title, &margined))
        return -1;

    uiGroup *g = uiNewGroup(title);
    if (g == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewGroup failed");
        return -1;
    }
    int rc = init_base(as_ctrl(self), uiControl(g));
    if (rc == 0 && margined)
        uiGroupSetMargined(g, 1);
    return rc;
}

static PyObject *
Group_get_title(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    char *t = uiGroupTitle(uiGroup(as_ctrl(self)->control));
    PyObject *s = PyUnicode_FromString(t);
    uiFreeText(t);
    return s;
}

static int
Group_set_title(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    const char *t = PyUnicode_AsUTF8(value);
    if (t == NULL) return -1;
    uiGroupSetTitle(uiGroup(as_ctrl(self)->control), t);
    return 0;
}

static PyObject *
Group_get_margined(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiGroupMargined(uiGroup(as_ctrl(self)->control)));
}

static int
Group_set_margined(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiGroupSetMargined(uiGroup(as_ctrl(self)->control), PyObject_IsTrue(value));
    return 0;
}

static PyObject *
Group_set_child(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *child_obj;
    if (!PyArg_ParseTuple(args, "O!", ControlType, &child_obj))
        return NULL;
    UiControlObject *self_c = as_ctrl(self);
    UiControlObject *child_c = as_ctrl(child_obj);
    if (check_control(self_c) < 0 || check_control(child_c) < 0
        || check_no_parent(child_c) < 0)
        return NULL;

    uiGroupSetChild(uiGroup(self_c->control), child_c->control);
    child_c->owned = 0;
    PyList_Append(self_c->children, child_obj);
    Py_RETURN_NONE;
}

static PyMethodDef Group_methods[] = {
    {"set_child", Group_set_child, METH_VARARGS,
     "set_child(child)\n--\n\nSet the group's child control."},
    {NULL}
};

static PyGetSetDef Group_getset[] = {
    {"title",    Group_get_title,    Group_set_title,
     "The group title.", NULL},
    {"margined", Group_get_margined, Group_set_margined,
     "Whether the group has a margin.", NULL},
    {NULL}
};

static PyType_Slot Group_slots[] = {
    {Py_tp_doc,       "Group(title, margined=True)\n--\n\n"
                      "A labeled container for grouping controls."},
    {Py_tp_init,      Group_init},
    {Py_tp_methods,   Group_methods},
    {Py_tp_getset,    Group_getset},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Group_spec = {
    .name      = "libui.core.Group",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Group_slots,
};
