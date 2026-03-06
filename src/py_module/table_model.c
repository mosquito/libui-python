/*
 * table_model.c — TableModel type wrapping uiTableModel + uiTableModelHandler.
 */
#include "module.h"

/* Forward declare Image struct from image.c */
typedef struct {
    PyObject_HEAD
    uiImage *image;
} UiImageObject;

/* Handler data — embedded handler + back-ref + Python callables */
typedef struct {
    uiTableModelHandler handler;  /* must be first */
    PyObject *self;               /* back-ref to Python TableModel */
} TableModelHandlerData;

typedef struct {
    PyObject_HEAD
    uiTableModel *model;
    TableModelHandlerData *handler_data;
    PyObject *callbacks;  /* dict of Python callables */
    PyObject *images;     /* list of Image refs for GC */
    UiResourceNode res_node;
} UiTableModelObject;

/* -- Handler trampolines ------------------------------------------- */

static int
tm_num_columns(uiTableModelHandler *mh, uiTableModel *m)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    TableModelHandlerData *data = (TableModelHandlerData *)mh;
    UiTableModelObject *self = (UiTableModelObject *)data->self;

    PyObject *cb = PyDict_GetItemString(self->callbacks, "num_columns");
    int result = 0;
    if (cb != NULL) {
        PyObject *ret = PyObject_CallNoArgs(cb);
        if (ret == NULL)
            PyErr_WriteUnraisable(cb);
        else {
            result = (int)PyLong_AsLong(ret);
            Py_DECREF(ret);
        }
    }
    PyGILState_Release(gstate);
    return result;
}

static uiTableValueType
tm_column_type(uiTableModelHandler *mh, uiTableModel *m, int column)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    TableModelHandlerData *data = (TableModelHandlerData *)mh;
    UiTableModelObject *self = (UiTableModelObject *)data->self;

    PyObject *cb = PyDict_GetItemString(self->callbacks, "column_type");
    uiTableValueType result = uiTableValueTypeString;
    if (cb != NULL) {
        PyObject *ret = PyObject_CallFunction(cb, "i", column);
        if (ret == NULL)
            PyErr_WriteUnraisable(cb);
        else {
            result = (uiTableValueType)PyLong_AsLong(ret);
            Py_DECREF(ret);
        }
    }
    PyGILState_Release(gstate);
    return result;
}

static int
tm_num_rows(uiTableModelHandler *mh, uiTableModel *m)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    TableModelHandlerData *data = (TableModelHandlerData *)mh;
    UiTableModelObject *self = (UiTableModelObject *)data->self;

    PyObject *cb = PyDict_GetItemString(self->callbacks, "num_rows");
    int result = 0;
    if (cb != NULL) {
        PyObject *ret = PyObject_CallNoArgs(cb);
        if (ret == NULL)
            PyErr_WriteUnraisable(cb);
        else {
            result = (int)PyLong_AsLong(ret);
            Py_DECREF(ret);
        }
    }
    PyGILState_Release(gstate);
    return result;
}

/* Convert Python value → uiTableValue* */
static uiTableValue *
python_to_table_value(PyObject *val, UiTableModelObject *self)
{
    if (val == Py_None)
        return NULL;

    if (PyUnicode_Check(val)) {
        const char *s = PyUnicode_AsUTF8(val);
        return uiNewTableValueString(s);
    }

    if (PyLong_Check(val)) {
        int i = (int)PyLong_AsLong(val);
        return uiNewTableValueInt(i);
    }

    /* Check for Image type */
    if (PyObject_TypeCheck(val, ImageType)) {
        UiImageObject *img = (UiImageObject *)val;
        /* Keep a strong ref to prevent GC while table uses the image */
        PyList_Append(self->images, val);
        return uiNewTableValueImage(img->image);
    }

    /* Check for (r, g, b, a) tuple */
    if (PyTuple_Check(val) && PyTuple_Size(val) == 4) {
        double r, g, b, a;
        if (PyArg_ParseTuple(val, "dddd", &r, &g, &b, &a))
            return uiNewTableValueColor(r, g, b, a);
        PyErr_Clear();
    }

    PyErr_SetString(PyExc_TypeError,
        "cell_value must return str, int, Image, (r,g,b,a) tuple, or None");
    return NULL;
}

static uiTableValue *
tm_cell_value(uiTableModelHandler *mh, uiTableModel *m, int row, int column)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    TableModelHandlerData *data = (TableModelHandlerData *)mh;
    UiTableModelObject *self = (UiTableModelObject *)data->self;

    PyObject *cb = PyDict_GetItemString(self->callbacks, "cell_value");
    uiTableValue *result = NULL;
    if (cb != NULL) {
        PyObject *ret = PyObject_CallFunction(cb, "ii", row, column);
        if (ret == NULL) {
            PyErr_WriteUnraisable(cb);
        } else {
            result = python_to_table_value(ret, self);
            if (result == NULL && PyErr_Occurred())
                PyErr_WriteUnraisable(cb);
            Py_DECREF(ret);
        }
    }
    PyGILState_Release(gstate);
    return result;
}

static void
tm_set_cell_value(uiTableModelHandler *mh, uiTableModel *m,
                  int row, int column, const uiTableValue *val)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    TableModelHandlerData *data = (TableModelHandlerData *)mh;
    UiTableModelObject *self = (UiTableModelObject *)data->self;

    PyObject *cb = PyDict_GetItemString(self->callbacks, "set_cell_value");
    if (cb == NULL || cb == Py_None) {
        PyGILState_Release(gstate);
        return;
    }

    /* Convert uiTableValue → Python */
    PyObject *py_val = Py_None;
    Py_INCREF(Py_None);

    if (val != NULL) {
        switch (uiTableValueGetType(val)) {
            case uiTableValueTypeString: {
                const char *s = uiTableValueString(val);
                Py_DECREF(py_val);
                py_val = PyUnicode_FromString(s);
                break;
            }
            case uiTableValueTypeInt: {
                int i = uiTableValueInt(val);
                Py_DECREF(py_val);
                py_val = PyLong_FromLong(i);
                break;
            }
            case uiTableValueTypeColor: {
                double r, g, b, a;
                uiTableValueColor(val, &r, &g, &b, &a);
                Py_DECREF(py_val);
                py_val = Py_BuildValue("(dddd)", r, g, b, a);
                break;
            }
            default:
                break;
        }
    }

    PyObject *result = PyObject_CallFunction(cb, "iiO", row, column, py_val);
    Py_DECREF(py_val);
    if (result == NULL)
        PyErr_WriteUnraisable(cb);
    else
        Py_DECREF(result);

    PyGILState_Release(gstate);
}

/* -- TableModel init ----------------------------------------------- */

static int
TableModel_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"num_columns", "column_type", "num_rows",
                             "cell_value", "set_cell_value", NULL};
    PyObject *num_columns_cb, *column_type_cb, *num_rows_cb;
    PyObject *cell_value_cb, *set_cell_value_cb = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOOO|O", kwlist,
                                     &num_columns_cb, &column_type_cb,
                                     &num_rows_cb, &cell_value_cb,
                                     &set_cell_value_cb))
        return -1;

    UiTableModelObject *m = (UiTableModelObject *)self;

    m->callbacks = PyDict_New();
    if (m->callbacks == NULL) return -1;
    m->images = PyList_New(0);
    if (m->images == NULL) return -1;

    /* Store callbacks */
    PyDict_SetItemString(m->callbacks, "num_columns", num_columns_cb);
    PyDict_SetItemString(m->callbacks, "column_type", column_type_cb);
    PyDict_SetItemString(m->callbacks, "num_rows", num_rows_cb);
    PyDict_SetItemString(m->callbacks, "cell_value", cell_value_cb);
    if (set_cell_value_cb != Py_None)
        PyDict_SetItemString(m->callbacks, "set_cell_value", set_cell_value_cb);

    /* Allocate handler data */
    m->handler_data = PyMem_Malloc(sizeof(TableModelHandlerData));
    if (m->handler_data == NULL) { PyErr_NoMemory(); return -1; }

    m->handler_data->handler.NumColumns = tm_num_columns;
    m->handler_data->handler.ColumnType = tm_column_type;
    m->handler_data->handler.NumRows = tm_num_rows;
    m->handler_data->handler.CellValue = tm_cell_value;
    m->handler_data->handler.SetCellValue = tm_set_cell_value;
    m->handler_data->self = self;

    m->model = uiNewTableModel(&m->handler_data->handler);
    if (m->model == NULL) {
        PyMem_Free(m->handler_data);
        m->handler_data = NULL;
        PyErr_SetString(PyExc_RuntimeError, "uiNewTableModel failed");
        return -1;
    }
    track_resource(&m->res_node, (void **)&m->model,
                   (resource_free_fn)uiFreeTableModel);

    return 0;
}

/* Methods */
static PyObject *
TableModel_row_inserted(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    int idx;
    if (!PyArg_ParseTuple(args, "i", &idx)) return NULL;
    UiTableModelObject *m = (UiTableModelObject *)self;
    uiTableModelRowInserted(m->model, idx);
    Py_RETURN_NONE;
}

static PyObject *
TableModel_row_changed(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    int idx;
    if (!PyArg_ParseTuple(args, "i", &idx)) return NULL;
    UiTableModelObject *m = (UiTableModelObject *)self;
    uiTableModelRowChanged(m->model, idx);
    Py_RETURN_NONE;
}

static PyObject *
TableModel_row_deleted(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    int idx;
    if (!PyArg_ParseTuple(args, "i", &idx)) return NULL;
    UiTableModelObject *m = (UiTableModelObject *)self;
    uiTableModelRowDeleted(m->model, idx);
    Py_RETURN_NONE;
}

static int
TableModel_traverse(PyObject *self, visitproc visit, void *arg)
{
    UiTableModelObject *m = (UiTableModelObject *)self;
    Py_VISIT(m->callbacks);
    Py_VISIT(m->images);
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static int
TableModel_clear(PyObject *self)
{
    UiTableModelObject *m = (UiTableModelObject *)self;
    Py_CLEAR(m->callbacks);
    Py_CLEAR(m->images);
    return 0;
}

static void
TableModel_dealloc(PyObject *self)
{
    UiTableModelObject *m = (UiTableModelObject *)self;
    PyObject_GC_UnTrack(self);
    untrack_resource(&m->res_node);
    TableModel_clear(self);
    if (m->model != NULL) {
        uiFreeTableModel(m->model);
        m->model = NULL;
    }
    if (m->handler_data != NULL) {
        PyMem_Free(m->handler_data);
        m->handler_data = NULL;
    }
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyMethodDef TableModel_methods[] = {
    {"row_inserted", TableModel_row_inserted, METH_VARARGS, "row_inserted(index)\n--\n\nNotify that a row was inserted."},
    {"row_changed",  TableModel_row_changed,  METH_VARARGS, "row_changed(index)\n--\n\nNotify that a row was changed."},
    {"row_deleted",  TableModel_row_deleted,  METH_VARARGS, "row_deleted(index)\n--\n\nNotify that a row was deleted."},
    {NULL}
};

static PyType_Slot TableModel_slots[] = {
    {Py_tp_doc,       "TableModel(num_columns, column_type, num_rows, cell_value, set_cell_value=None)\n--\n\nA data model for Table, backed by Python callbacks."},
    {Py_tp_init,      TableModel_init},
    {Py_tp_methods,   TableModel_methods},
    {Py_tp_dealloc,   TableModel_dealloc},
    {Py_tp_traverse,  TableModel_traverse},
    {Py_tp_clear,     TableModel_clear},
    {0, NULL}
};

PyType_Spec TableModel_spec = {
    .name      = "libui.core.TableModel",
    .basicsize = sizeof(UiTableModelObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = TableModel_slots,
};
