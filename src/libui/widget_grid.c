/* widget_grid.c — Grid type. */
#include "module.h"

static int
Grid_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"padded", NULL};
    int padded = 1;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|p", kwlist, &padded))
        return -1;

    uiGrid *g = uiNewGrid();
    if (g == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewGrid failed");
        return -1;
    }
    int rc = init_base(as_ctrl(self), uiControl(g));
    if (rc == 0 && padded)
        uiGridSetPadded(g, 1);
    return rc;
}

static PyObject *
Grid_append(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {
        "child", "left", "top", "xspan", "yspan",
        "hexpand", "halign", "vexpand", "valign", NULL
    };
    PyObject *child_obj;
    int left, top, xspan = 1, yspan = 1;
    int hexpand = 0, halign = uiAlignFill;
    int vexpand = 0, valign = uiAlignFill;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "O!ii|iipipi", kwlist,
            ControlType, &child_obj,
            &left, &top, &xspan, &yspan,
            &hexpand, &halign, &vexpand, &valign))
        return NULL;

    UiControlObject *self_c = as_ctrl(self);
    UiControlObject *child_c = as_ctrl(child_obj);
    if (check_control(self_c) < 0 || check_control(child_c) < 0)
        return NULL;

    uiGridAppend(uiGrid(self_c->control), child_c->control,
                 left, top, xspan, yspan,
                 hexpand, (uiAlign)halign, vexpand, (uiAlign)valign);
    child_c->owned = 0;
    PyList_Append(self_c->children, child_obj);
    Py_RETURN_NONE;
}

static PyObject *
Grid_insert_at(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {
        "child", "existing", "at", "xspan", "yspan",
        "hexpand", "halign", "vexpand", "valign", NULL
    };
    PyObject *child_obj;
    PyObject *existing_obj;
    int at, xspan = 1, yspan = 1;
    int hexpand = 0, halign = uiAlignFill;
    int vexpand = 0, valign = uiAlignFill;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "O!O!i|iipipi", kwlist,
            ControlType, &child_obj, ControlType, &existing_obj,
            &at, &xspan, &yspan,
            &hexpand, &halign, &vexpand, &valign))
        return NULL;

    UiControlObject *self_c = as_ctrl(self);
    UiControlObject *child_c = as_ctrl(child_obj);
    UiControlObject *exist_c = as_ctrl(existing_obj);
    if (check_control(self_c) < 0 || check_control(child_c) < 0
        || check_control(exist_c) < 0)
        return NULL;

    uiGridInsertAt(uiGrid(self_c->control), child_c->control,
                   exist_c->control, (uiAt)at,
                   xspan, yspan,
                   hexpand, (uiAlign)halign, vexpand, (uiAlign)valign);
    child_c->owned = 0;
    PyList_Append(self_c->children, child_obj);
    Py_RETURN_NONE;
}

static PyObject *
Grid_get_padded(PyObject *self, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiGridPadded(uiGrid(as_ctrl(self)->control)));
}

static int
Grid_set_padded(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiGridSetPadded(uiGrid(as_ctrl(self)->control), PyObject_IsTrue(value));
    return 0;
}

static PyMethodDef Grid_methods[] = {
    {"append",    (PyCFunction)Grid_append,    METH_VARARGS | METH_KEYWORDS,
     "append(child, left, top, xspan=1, yspan=1, hexpand=False, halign=Align.FILL, vexpand=False, valign=Align.FILL)\n--\n\nAdd a child to the grid."},
    {"insert_at", (PyCFunction)Grid_insert_at, METH_VARARGS | METH_KEYWORDS,
     "insert_at(child, existing, at, xspan=1, yspan=1, ...)\n--\n\nInsert a child relative to an existing one."},
    {NULL}
};

static PyGetSetDef Grid_getset[] = {
    {"padded", Grid_get_padded, Grid_set_padded,
     "Whether the grid has padding between cells.", NULL},
    {NULL}
};

static PyType_Slot Grid_slots[] = {
    {Py_tp_doc,       "Grid(padded=True)\n--\n\n"
                      "A grid layout container."},
    {Py_tp_init,      Grid_init},
    {Py_tp_methods,   Grid_methods},
    {Py_tp_getset,    Grid_getset},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Grid_spec = {
    .name      = "libui.core.Grid",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Grid_slots,
};
