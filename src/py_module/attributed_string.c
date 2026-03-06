/*
 * attributed_string.c — AttributedString type.
 */
#include "module.h"

/* Forward declaration of UiAttributeObject from attribute.c */
typedef struct {
    PyObject_HEAD
    uiAttribute *attr;
    int owned;
    UiResourceNode res_node;
} UiAttributeObject;

typedef struct {
    PyObject_HEAD
    uiAttributedString *str;
    PyObject *attributes;  /* list — prevent GC of consumed Attributes */
    UiResourceNode res_node;
} UiAttributedStringObject;

static int
AStr_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"text", NULL};
    const char *text;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &text))
        return -1;

    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    s->str = uiNewAttributedString(text);
    if (s->str == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewAttributedString failed");
        return -1;
    }
    s->attributes = PyList_New(0);
    if (s->attributes == NULL) return -1;
    track_resource(&s->res_node, (void **)&s->str,
                   (resource_free_fn)uiFreeAttributedString);
    return 0;
}

/* Properties */
static PyObject *
AStr_get_string(PyObject *self, void *closure)
{
    ENSURE_MAIN_THREAD;
    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    return PyUnicode_FromString(uiAttributedStringString(s->str));
}

static PyObject *
AStr_get_length(PyObject *self, void *closure)
{
    ENSURE_MAIN_THREAD;
    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    return PyLong_FromSize_t(uiAttributedStringLen(s->str));
}

/* Methods */
static PyObject *
AStr_append(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    const char *text;
    if (!PyArg_ParseTuple(args, "s", &text)) return NULL;
    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    uiAttributedStringAppendUnattributed(s->str, text);
    Py_RETURN_NONE;
}

static PyObject *
AStr_insert_at(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    const char *text;
    Py_ssize_t pos;
    if (!PyArg_ParseTuple(args, "sn", &text, &pos)) return NULL;
    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    size_t len = uiAttributedStringLen(s->str);
    if (pos < 0 || (size_t)pos > len) {
        PyErr_SetString(PyExc_IndexError, "insert position out of range");
        return NULL;
    }
    uiAttributedStringInsertAtUnattributed(s->str, text, (size_t)pos);
    Py_RETURN_NONE;
}

static PyObject *
AStr_delete(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    Py_ssize_t start, end;
    if (!PyArg_ParseTuple(args, "nn", &start, &end)) return NULL;
    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    size_t len = uiAttributedStringLen(s->str);
    if (start < 0 || end < 0 || (size_t)start > len || (size_t)end > len || start > end) {
        PyErr_SetString(PyExc_IndexError, "delete range out of bounds");
        return NULL;
    }
    uiAttributedStringDelete(s->str, (size_t)start, (size_t)end);
    Py_RETURN_NONE;
}

static PyObject *
AStr_set_attribute(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *attr_obj;
    Py_ssize_t start, end;
    if (!PyArg_ParseTuple(args, "O!nn", AttributeType, &attr_obj, &start, &end))
        return NULL;

    UiAttributeObject *attr = (UiAttributeObject *)attr_obj;
    if (!attr->owned) {
        PyErr_SetString(PyExc_RuntimeError,
            "attribute has already been consumed by an AttributedString");
        return NULL;
    }

    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    uiAttributedStringSetAttribute(s->str, attr->attr, (size_t)start, (size_t)end);
    attr->owned = 0;  /* AttributedString now owns it */
    untrack_resource(&attr->res_node);  /* no longer independently freeable */

    /* Keep a reference to prevent GC */
    PyList_Append(s->attributes, attr_obj);
    Py_RETURN_NONE;
}

/* ForEach callback data */
typedef struct {
    PyObject *callback;
    int error;
} AStr_ForEach_Data;

static uiForEach
astr_foreach_cb(const uiAttributedString *s, const uiAttribute *a,
                size_t start, size_t end, void *data)
{
    AStr_ForEach_Data *fed = (AStr_ForEach_Data *)data;
    if (fed->error) return uiForEachStop;

    /* Create a temporary non-owned Attribute wrapper */
    UiAttributeObject *attr_obj = PyObject_GC_New(UiAttributeObject, AttributeType);
    if (attr_obj == NULL) { fed->error = 1; return uiForEachStop; }
    attr_obj->attr = (uiAttribute *)a;  /* const cast — read-only use */
    attr_obj->owned = 0;  /* Do NOT free on dealloc */
    attr_obj->res_node.res_prev = NULL;  /* not tracked */
    attr_obj->res_node.res_next = NULL;
    PyObject_GC_Track((PyObject *)attr_obj);

    PyObject *result = PyObject_CallFunction(
        fed->callback, "Onn", attr_obj, (Py_ssize_t)start, (Py_ssize_t)end);
    Py_DECREF(attr_obj);

    if (result == NULL) {
        fed->error = 1;
        return uiForEachStop;
    }
    int stop = PyObject_IsTrue(result);
    Py_DECREF(result);
    return stop ? uiForEachStop : uiForEachContinue;
}

static PyObject *
AStr_for_each_attribute(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *callback;
    if (!PyArg_ParseTuple(args, "O", &callback)) return NULL;
    if (!PyCallable_Check(callback)) {
        PyErr_SetString(PyExc_TypeError, "callback must be callable");
        return NULL;
    }
    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    AStr_ForEach_Data fed = { callback, 0 };
    uiAttributedStringForEachAttribute(s->str, astr_foreach_cb, &fed);
    if (fed.error && PyErr_Occurred()) return NULL;
    Py_RETURN_NONE;
}

static PyObject *
AStr_num_graphemes(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    return PyLong_FromSize_t(uiAttributedStringNumGraphemes(s->str));
}

static PyObject *
AStr_byte_index_to_grapheme(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    Py_ssize_t pos;
    if (!PyArg_ParseTuple(args, "n", &pos)) return NULL;
    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    return PyLong_FromSize_t(uiAttributedStringByteIndexToGrapheme(s->str, (size_t)pos));
}

static PyObject *
AStr_grapheme_to_byte_index(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    Py_ssize_t pos;
    if (!PyArg_ParseTuple(args, "n", &pos)) return NULL;
    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    return PyLong_FromSize_t(uiAttributedStringGraphemeToByteIndex(s->str, (size_t)pos));
}

/* GC */
static int
AStr_traverse(PyObject *self, visitproc visit, void *arg)
{
    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    Py_VISIT(s->attributes);
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static int
AStr_clear(PyObject *self)
{
    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    Py_CLEAR(s->attributes);
    return 0;
}

static void
AStr_dealloc(PyObject *self)
{
    UiAttributedStringObject *s = (UiAttributedStringObject *)self;
    PyObject_GC_UnTrack(self);
    untrack_resource(&s->res_node);
    AStr_clear(self);
    if (s->str != NULL) {
        uiFreeAttributedString(s->str);
        s->str = NULL;
    }
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyMethodDef AStr_methods[] = {
    {"append",                   AStr_append,                   METH_VARARGS, "append(text)\n--\n\nAppend unattributed text."},
    {"insert_at",                AStr_insert_at,                METH_VARARGS, "insert_at(text, pos)\n--\n\nInsert unattributed text at byte position."},
    {"delete",                   AStr_delete,                   METH_VARARGS, "delete(start, end)\n--\n\nDelete the byte range [start, end)."},
    {"set_attribute",            AStr_set_attribute,            METH_VARARGS, "set_attribute(attr, start, end)\n--\n\nApply an attribute to the byte range [start, end)."},
    {"for_each_attribute",       AStr_for_each_attribute,       METH_VARARGS, "for_each_attribute(callback)\n--\n\nIterate attributes. Callback receives (attr, start, end)."},
    {"num_graphemes",            AStr_num_graphemes,            METH_NOARGS,  "Return the number of grapheme clusters."},
    {"byte_index_to_grapheme",   AStr_byte_index_to_grapheme,   METH_VARARGS, "byte_index_to_grapheme(pos)\n--\n\nConvert byte index to grapheme index."},
    {"grapheme_to_byte_index",   AStr_grapheme_to_byte_index,   METH_VARARGS, "grapheme_to_byte_index(pos)\n--\n\nConvert grapheme index to byte index."},
    {NULL}
};

static PyGetSetDef AStr_getset[] = {
    {"string", AStr_get_string, NULL, "The plain text content.", NULL},
    {"length", AStr_get_length, NULL, "The byte length of the string.", NULL},
    {NULL}
};

static PyType_Slot AStr_slots[] = {
    {Py_tp_doc,       "AttributedString(text)\n--\n\nA string with formatting attributes."},
    {Py_tp_init,      AStr_init},
    {Py_tp_methods,   AStr_methods},
    {Py_tp_getset,    AStr_getset},
    {Py_tp_dealloc,   AStr_dealloc},
    {Py_tp_traverse,  AStr_traverse},
    {Py_tp_clear,     AStr_clear},
    {0, NULL}
};

PyType_Spec AttributedString_spec = {
    .name      = "libui.core.AttributedString",
    .basicsize = sizeof(UiAttributedStringObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = AStr_slots,
};
