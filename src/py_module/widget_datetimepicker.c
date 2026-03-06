/* widget_datetimepicker.c — DateTimePicker type. */
#include "module.h"
#include <time.h>

static int
DateTimePicker_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"type", NULL};
    const char *type = "datetime";
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|s", kwlist, &type))
        return -1;

    uiDateTimePicker *d;
    if (strcmp(type, "date") == 0)
        d = uiNewDatePicker();
    else if (strcmp(type, "time") == 0)
        d = uiNewTimePicker();
    else
        d = uiNewDateTimePicker();

    if (d == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewDateTimePicker failed");
        return -1;
    }
    return init_base(as_ctrl(self), uiControl(d));
}

static PyObject *
DateTimePicker_get_time(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;

    struct tm t;
    memset(&t, 0, sizeof(t));
    uiDateTimePickerTime(
        uiDateTimePicker(as_ctrl(self)->control), &t);

    PyObject *datetime_mod = PyImport_ImportModule("datetime");
    if (datetime_mod == NULL) return NULL;

    PyObject *dt = PyObject_CallMethod(
        datetime_mod, "datetime", "iiiiiii",
        t.tm_year + 1900, t.tm_mon + 1, t.tm_mday,
        t.tm_hour, t.tm_min, t.tm_sec, 0);
    Py_DECREF(datetime_mod);
    return dt;
}

static int
DateTimePicker_set_time(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD_INT;
    if (check_control(as_ctrl(self)) < 0) return -1;

    PyObject *datetime_mod = PyImport_ImportModule("datetime");
    if (datetime_mod == NULL) return -1;
    PyObject *datetime_cls = PyObject_GetAttrString(datetime_mod, "datetime");
    Py_DECREF(datetime_mod);
    if (datetime_cls == NULL) return -1;

    int is_dt = PyObject_IsInstance(value, datetime_cls);
    Py_DECREF(datetime_cls);
    if (is_dt < 0) return -1;
    if (!is_dt) {
        PyErr_SetString(PyExc_TypeError,
                        "expected a datetime.datetime instance");
        return -1;
    }

    struct tm t;
    memset(&t, 0, sizeof(t));

    PyObject *tmp;
    tmp = PyObject_GetAttrString(value, "year");
    if (!tmp) return -1;
    t.tm_year = (int)PyLong_AsLong(tmp) - 1900;
    Py_DECREF(tmp);

    tmp = PyObject_GetAttrString(value, "month");
    if (!tmp) return -1;
    t.tm_mon = (int)PyLong_AsLong(tmp) - 1;
    Py_DECREF(tmp);

    tmp = PyObject_GetAttrString(value, "day");
    if (!tmp) return -1;
    t.tm_mday = (int)PyLong_AsLong(tmp);
    Py_DECREF(tmp);

    tmp = PyObject_GetAttrString(value, "hour");
    if (!tmp) return -1;
    t.tm_hour = (int)PyLong_AsLong(tmp);
    Py_DECREF(tmp);

    tmp = PyObject_GetAttrString(value, "minute");
    if (!tmp) return -1;
    t.tm_min = (int)PyLong_AsLong(tmp);
    Py_DECREF(tmp);

    tmp = PyObject_GetAttrString(value, "second");
    if (!tmp) return -1;
    t.tm_sec = (int)PyLong_AsLong(tmp);
    Py_DECREF(tmp);

    uiDateTimePickerSetTime(
        uiDateTimePicker(as_ctrl(self)->control), &t);
    return 0;
}

static PyObject *
DateTimePicker_on_changed(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    UiControlObject *c = as_ctrl(self);
    if (check_control(c) < 0) return NULL;
    if (store_callback(c, "on_changed", callable) < 0) return NULL;
    uiDateTimePickerOnChanged(
        uiDateTimePicker(c->control),
        (void (*)(uiDateTimePicker *, void *))trampoline_void,
        callable);
    Py_RETURN_NONE;
}

static PyMethodDef DateTimePicker_methods[] = {
    {"on_changed", DateTimePicker_on_changed, METH_VARARGS,
     "Register a callback for when the value changes."},
    {NULL}
};

static PyGetSetDef DateTimePicker_getset[] = {
    {"time", DateTimePicker_get_time, DateTimePicker_set_time,
     "The current value as a datetime.datetime object.", NULL},
    {NULL}
};

static PyType_Slot DateTimePicker_slots[] = {
    {Py_tp_init,      DateTimePicker_init},
    {Py_tp_methods,   DateTimePicker_methods},
    {Py_tp_getset,    DateTimePicker_getset},
    {Py_tp_doc,       "DateTimePicker(type='datetime')\n--\n\n"
                      "A date/time picker. Type can be 'datetime', 'date', or 'time'."},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec DateTimePicker_spec = {
    .name      = "libui.core.DateTimePicker",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = DateTimePicker_slots,
};
