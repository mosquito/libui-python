/*
 * widget_table.c — Table type (Control subclass).
 */
#include "module.h"

/* Forward declare TableModel struct from table_model.c */
typedef struct {
    PyObject_HEAD
    uiTableModel *model;
    void *handler_data;
    PyObject *callbacks;
    PyObject *images;
} UiTableModelObject;

/* -- Table row/column callback trampolines -------------------------- */

static void
table_row_trampoline(uiTable *t, int row, void *data)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *callable = (PyObject *)data;
    PyObject *result = PyObject_CallFunction(callable, "i", row);
    if (result == NULL)
        PyErr_WriteUnraisable(callable);
    else
        Py_DECREF(result);
    PyGILState_Release(gstate);
}

static void
table_void_trampoline(uiTable *t, void *data)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *callable = (PyObject *)data;
    PyObject *result = PyObject_CallNoArgs(callable);
    if (result == NULL)
        PyErr_WriteUnraisable(callable);
    else
        Py_DECREF(result);
    PyGILState_Release(gstate);
}

static void
table_column_trampoline(uiTable *t, int column, void *data)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *callable = (PyObject *)data;
    PyObject *result = PyObject_CallFunction(callable, "i", column);
    if (result == NULL)
        PyErr_WriteUnraisable(callable);
    else
        Py_DECREF(result);
    PyGILState_Release(gstate);
}

/* -- Table_init ---------------------------------------------------- */

static int
Table_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"model", "row_background_color_column", NULL};
    PyObject *model_obj;
    int bg_col = -1;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|i", kwlist,
                                     TableModelType, &model_obj, &bg_col))
        return -1;

    UiTableModelObject *model = (UiTableModelObject *)model_obj;

    uiTableParams params;
    params.Model = model->model;
    params.RowBackgroundColorModelColumn = bg_col;

    uiTable *t = uiNewTable(&params);
    if (init_base(as_ctrl(self), uiControl(t)) < 0)
        return -1;

    /* Keep a strong ref to the model */
    PyList_Append(as_ctrl(self)->children, model_obj);

    return 0;
}

/* -- Column append methods ----------------------------------------- */

static PyObject *
Table_append_text_column(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"name", "text_col", "editable_col", "color_col", NULL};
    const char *name;
    int text_col, editable_col = -1, color_col = -1;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "si|ii", kwlist,
                                     &name, &text_col, &editable_col, &color_col))
        return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;

    uiTableTextColumnOptionalParams tp;
    tp.ColorModelColumn = color_col;

    uiTableAppendTextColumn(uiTable(as_ctrl(self)->control),
                            name, text_col, editable_col,
                            color_col >= 0 ? &tp : NULL);
    Py_RETURN_NONE;
}

static PyObject *
Table_append_image_column(PyObject *self, PyObject *args)
{
    const char *name;
    int img_col;
    if (!PyArg_ParseTuple(args, "si", &name, &img_col)) return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiTableAppendImageColumn(uiTable(as_ctrl(self)->control), name, img_col);
    Py_RETURN_NONE;
}

static PyObject *
Table_append_image_text_column(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"name", "img_col", "text_col", "editable_col", "color_col", NULL};
    const char *name;
    int img_col, text_col, editable_col = -1, color_col = -1;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "sii|ii", kwlist,
                                     &name, &img_col, &text_col,
                                     &editable_col, &color_col))
        return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;

    uiTableTextColumnOptionalParams tp;
    tp.ColorModelColumn = color_col;

    uiTableAppendImageTextColumn(uiTable(as_ctrl(self)->control),
                                 name, img_col, text_col, editable_col,
                                 color_col >= 0 ? &tp : NULL);
    Py_RETURN_NONE;
}

static PyObject *
Table_append_checkbox_column(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"name", "checkbox_col", "editable_col", NULL};
    const char *name;
    int checkbox_col, editable_col = -1;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "si|i", kwlist,
                                     &name, &checkbox_col, &editable_col))
        return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiTableAppendCheckboxColumn(uiTable(as_ctrl(self)->control),
                                name, checkbox_col, editable_col);
    Py_RETURN_NONE;
}

static PyObject *
Table_append_checkbox_text_column(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"name", "checkbox_col", "checkbox_editable_col",
                             "text_col", "text_editable_col", "color_col", NULL};
    const char *name;
    int cb_col, cb_edit_col, text_col, text_edit_col = -1, color_col = -1;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "siii|ii", kwlist,
                                     &name, &cb_col, &cb_edit_col,
                                     &text_col, &text_edit_col, &color_col))
        return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;

    uiTableTextColumnOptionalParams tp;
    tp.ColorModelColumn = color_col;

    uiTableAppendCheckboxTextColumn(uiTable(as_ctrl(self)->control),
                                    name, cb_col, cb_edit_col,
                                    text_col, text_edit_col,
                                    color_col >= 0 ? &tp : NULL);
    Py_RETURN_NONE;
}

static PyObject *
Table_append_progress_bar_column(PyObject *self, PyObject *args)
{
    const char *name;
    int col;
    if (!PyArg_ParseTuple(args, "si", &name, &col)) return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiTableAppendProgressBarColumn(uiTable(as_ctrl(self)->control), name, col);
    Py_RETURN_NONE;
}

static PyObject *
Table_append_button_column(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"name", "btn_col", "clickable_col", NULL};
    const char *name;
    int btn_col, clickable_col = -1;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "si|i", kwlist,
                                     &name, &btn_col, &clickable_col))
        return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiTableAppendButtonColumn(uiTable(as_ctrl(self)->control),
                              name, btn_col, clickable_col);
    Py_RETURN_NONE;
}

/* -- Properties ---------------------------------------------------- */

static PyObject *
Table_get_header_visible(PyObject *self, void *closure)
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiTableHeaderVisible(uiTable(as_ctrl(self)->control)));
}

static int
Table_set_header_visible(PyObject *self, PyObject *value, void *closure)
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    uiTableHeaderSetVisible(uiTable(as_ctrl(self)->control),
                            PyObject_IsTrue(value));
    return 0;
}

static PyObject *
Table_get_selection_mode(PyObject *self, void *closure)
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyLong_FromLong(uiTableGetSelectionMode(uiTable(as_ctrl(self)->control)));
}

static int
Table_set_selection_mode(PyObject *self, PyObject *value, void *closure)
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    int mode = (int)PyLong_AsLong(value);
    if (mode == -1 && PyErr_Occurred()) return -1;
    uiTableSetSelectionMode(uiTable(as_ctrl(self)->control),
                            (uiTableSelectionMode)mode);
    return 0;
}

static PyObject *
Table_get_selection(PyObject *self, void *closure)
{
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiTableSelection *sel = uiTableGetSelection(uiTable(as_ctrl(self)->control));
    PyObject *list = PyList_New(sel->NumRows);
    if (list == NULL) {
        uiFreeTableSelection(sel);
        return NULL;
    }
    for (int i = 0; i < sel->NumRows; i++)
        PyList_SET_ITEM(list, i, PyLong_FromLong(sel->Rows[i]));
    uiFreeTableSelection(sel);
    return list;
}

static int
Table_set_selection(PyObject *self, PyObject *value, void *closure)
{
    if (check_control(as_ctrl(self)) < 0) return -1;
    if (!PyList_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "selection must be a list of int");
        return -1;
    }

    Py_ssize_t n = PyList_Size(value);
    uiTableSelection sel;
    sel.NumRows = (int)n;

    int *rows = NULL;
    if (n > 0) {
        rows = PyMem_Malloc(sizeof(int) * n);
        if (rows == NULL) { PyErr_NoMemory(); return -1; }
        for (Py_ssize_t i = 0; i < n; i++) {
            rows[i] = (int)PyLong_AsLong(PyList_GetItem(value, i));
            if (rows[i] == -1 && PyErr_Occurred()) {
                PyMem_Free(rows);
                return -1;
            }
        }
    }
    sel.Rows = rows;

    uiTableSetSelection(uiTable(as_ctrl(self)->control), &sel);
    if (rows) PyMem_Free(rows);
    return 0;
}

/* -- Callback registrations ---------------------------------------- */

static PyObject *
Table_on_row_clicked(PyObject *self, PyObject *args)
{
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable)) return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_row_clicked", callable) < 0) return NULL;
    uiTableOnRowClicked(uiTable(c->control), table_row_trampoline, callable);
    Py_RETURN_NONE;
}

static PyObject *
Table_on_row_double_clicked(PyObject *self, PyObject *args)
{
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable)) return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_row_double_clicked", callable) < 0) return NULL;
    uiTableOnRowDoubleClicked(uiTable(c->control), table_row_trampoline, callable);
    Py_RETURN_NONE;
}

static PyObject *
Table_on_selection_changed(PyObject *self, PyObject *args)
{
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable)) return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_selection_changed", callable) < 0) return NULL;
    uiTableOnSelectionChanged(uiTable(c->control), table_void_trampoline, callable);
    Py_RETURN_NONE;
}

static PyObject *
Table_on_header_clicked(PyObject *self, PyObject *args)
{
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable)) return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_header_clicked", callable) < 0) return NULL;
    uiTableHeaderOnClicked(uiTable(c->control), table_column_trampoline, callable);
    Py_RETURN_NONE;
}

/* -- Header sort indicator / column width methods ------------------ */

static PyObject *
Table_header_sort_indicator(PyObject *self, PyObject *args)
{
    int col;
    if (!PyArg_ParseTuple(args, "i", &col)) return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyLong_FromLong(
        uiTableHeaderSortIndicator(uiTable(as_ctrl(self)->control), col));
}

static PyObject *
Table_header_set_sort_indicator(PyObject *self, PyObject *args)
{
    int col, indicator;
    if (!PyArg_ParseTuple(args, "ii", &col, &indicator)) return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiTableHeaderSetSortIndicator(uiTable(as_ctrl(self)->control),
                                  col, (uiSortIndicator)indicator);
    Py_RETURN_NONE;
}

static PyObject *
Table_column_width(PyObject *self, PyObject *args)
{
    int col;
    if (!PyArg_ParseTuple(args, "i", &col)) return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyLong_FromLong(
        uiTableColumnWidth(uiTable(as_ctrl(self)->control), col));
}

static PyObject *
Table_set_column_width(PyObject *self, PyObject *args)
{
    int col, width;
    if (!PyArg_ParseTuple(args, "ii", &col, &width)) return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiTableColumnSetWidth(uiTable(as_ctrl(self)->control), col, width);
    Py_RETURN_NONE;
}

/* -- Type definition ----------------------------------------------- */

static PyMethodDef Table_methods[] = {
    {"append_text_column",          (PyCFunction)Table_append_text_column,          METH_VARARGS | METH_KEYWORDS, "append_text_column(name, text_col, editable_col=-1, color_col=-1)"},
    {"append_image_column",         Table_append_image_column,                      METH_VARARGS,                 "append_image_column(name, img_col)"},
    {"append_image_text_column",    (PyCFunction)Table_append_image_text_column,    METH_VARARGS | METH_KEYWORDS, "append_image_text_column(name, img_col, text_col, ...)"},
    {"append_checkbox_column",      (PyCFunction)Table_append_checkbox_column,      METH_VARARGS | METH_KEYWORDS, "append_checkbox_column(name, checkbox_col, editable_col=-1)"},
    {"append_checkbox_text_column", (PyCFunction)Table_append_checkbox_text_column, METH_VARARGS | METH_KEYWORDS, "append_checkbox_text_column(name, cb_col, cb_editable_col, text_col, ...)"},
    {"append_progress_bar_column",  Table_append_progress_bar_column,               METH_VARARGS,                 "append_progress_bar_column(name, col)"},
    {"append_button_column",        (PyCFunction)Table_append_button_column,        METH_VARARGS | METH_KEYWORDS, "append_button_column(name, btn_col, clickable_col=-1)"},
    {"on_row_clicked",              Table_on_row_clicked,                            METH_VARARGS,                 "Register a callback for row click. Receives row index."},
    {"on_row_double_clicked",       Table_on_row_double_clicked,                     METH_VARARGS,                 "Register a callback for row double-click."},
    {"on_selection_changed",        Table_on_selection_changed,                       METH_VARARGS,                 "Register a callback for selection changes."},
    {"on_header_clicked",           Table_on_header_clicked,                          METH_VARARGS,                 "Register a callback for header click. Receives column index."},
    {"header_sort_indicator",       Table_header_sort_indicator,                      METH_VARARGS,                 "header_sort_indicator(col)\n--\n\nGet the sort indicator for a column."},
    {"header_set_sort_indicator",   Table_header_set_sort_indicator,                  METH_VARARGS,                 "header_set_sort_indicator(col, indicator)\n--\n\nSet the sort indicator."},
    {"column_width",                Table_column_width,                               METH_VARARGS,                 "column_width(col)\n--\n\nGet a column width."},
    {"set_column_width",            Table_set_column_width,                           METH_VARARGS,                 "set_column_width(col, width)\n--\n\nSet a column width."},
    {NULL}
};

static PyGetSetDef Table_getset[] = {
    {"header_visible",  Table_get_header_visible,  Table_set_header_visible,  "Whether the header row is visible.", NULL},
    {"selection_mode",  Table_get_selection_mode,   Table_set_selection_mode,  "The selection mode (SelectionMode enum).", NULL},
    {"selection",       Table_get_selection,        Table_set_selection,       "List of selected row indices.", NULL},
    {NULL}
};

static PyType_Slot Table_slots[] = {
    {Py_tp_doc,       "Table(model, row_background_color_column=-1)\n--\n\nA data table control."},
    {Py_tp_init,      Table_init},
    {Py_tp_methods,   Table_methods},
    {Py_tp_getset,    Table_getset},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Table_spec = {
    .name      = "libui.core.Table",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Table_slots,
};

/* -- Table enums --------------------------------------------------- */

static const EnumMember table_value_type_members[] = {
    {"STRING", uiTableValueTypeString},
    {"IMAGE",  uiTableValueTypeImage},
    {"INT",    uiTableValueTypeInt},
    {"COLOR",  uiTableValueTypeColor},
};

static const EnumMember table_model_column_members[] = {
    {"NEVER_EDITABLE",  uiTableModelColumnNeverEditable},
    {"ALWAYS_EDITABLE", uiTableModelColumnAlwaysEditable},
};

static const EnumMember selection_mode_members[] = {
    {"NONE",         uiTableSelectionModeNone},
    {"ZERO_OR_ONE",  uiTableSelectionModeZeroOrOne},
    {"ONE",          uiTableSelectionModeOne},
    {"ZERO_OR_MANY", uiTableSelectionModeZeroOrMany},
};

static const EnumMember sort_indicator_members[] = {
    {"NONE",       uiSortIndicatorNone},
    {"ASCENDING",  uiSortIndicatorAscending},
    {"DESCENDING", uiSortIndicatorDescending},
};

static const EnumMember for_each_members[] = {
    {"CONTINUE", uiForEachContinue},
    {"STOP",     uiForEachStop},
};

int
register_table_enums(PyObject *module, PyObject *IntEnum)
{
    if (add_enum(module, IntEnum, "TableValueType",
                 table_value_type_members, N_MEMBERS(table_value_type_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "TableModelColumn",
                 table_model_column_members, N_MEMBERS(table_model_column_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "SelectionMode",
                 selection_mode_members, N_MEMBERS(selection_mode_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "SortIndicator",
                 sort_indicator_members, N_MEMBERS(sort_indicator_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "ForEach",
                 for_each_members, N_MEMBERS(for_each_members)) < 0) return -1;
    return 0;
}
