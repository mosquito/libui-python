/*
 * attribute.c — OpenTypeFeatures + Attribute types, plus factory functions.
 */
#include "module.h"

/* -- OpenTypeFeatures ---------------------------------------------- */

typedef struct {
    PyObject_HEAD
    uiOpenTypeFeatures *otf;
    int owned;  /* 0 if belongs to an Attribute */
} UiOpenTypeFeaturesObject;

static int
parse_tag(const char *tag, Py_ssize_t len, char *a, char *b, char *c, char *d)
{
    if (len != 4) {
        PyErr_SetString(PyExc_ValueError, "OpenType tag must be exactly 4 characters");
        return -1;
    }
    *a = tag[0]; *b = tag[1]; *c = tag[2]; *d = tag[3];
    return 0;
}

static int
OTF_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    if (!PyArg_ParseTuple(args, ""))
        return -1;
    UiOpenTypeFeaturesObject *o = (UiOpenTypeFeaturesObject *)self;
    o->otf = uiNewOpenTypeFeatures();
    o->owned = 1;
    return 0;
}

static PyObject *
OTF_add(PyObject *self, PyObject *args)
{
    const char *tag;
    Py_ssize_t tag_len;
    unsigned int value;
    if (!PyArg_ParseTuple(args, "s#I", &tag, &tag_len, &value))
        return NULL;
    char a, b, c, d;
    if (parse_tag(tag, tag_len, &a, &b, &c, &d) < 0) return NULL;
    UiOpenTypeFeaturesObject *o = (UiOpenTypeFeaturesObject *)self;
    uiOpenTypeFeaturesAdd(o->otf, a, b, c, d, value);
    Py_RETURN_NONE;
}

static PyObject *
OTF_remove(PyObject *self, PyObject *args)
{
    const char *tag;
    Py_ssize_t tag_len;
    if (!PyArg_ParseTuple(args, "s#", &tag, &tag_len))
        return NULL;
    char a, b, c, d;
    if (parse_tag(tag, tag_len, &a, &b, &c, &d) < 0) return NULL;
    UiOpenTypeFeaturesObject *o = (UiOpenTypeFeaturesObject *)self;
    uiOpenTypeFeaturesRemove(o->otf, a, b, c, d);
    Py_RETURN_NONE;
}

static PyObject *
OTF_get(PyObject *self, PyObject *args)
{
    const char *tag;
    Py_ssize_t tag_len;
    if (!PyArg_ParseTuple(args, "s#", &tag, &tag_len))
        return NULL;
    char a, b, c, d;
    if (parse_tag(tag, tag_len, &a, &b, &c, &d) < 0) return NULL;
    UiOpenTypeFeaturesObject *o = (UiOpenTypeFeaturesObject *)self;
    uint32_t value;
    if (uiOpenTypeFeaturesGet(o->otf, a, b, c, d, &value))
        return PyLong_FromUnsignedLong(value);
    Py_RETURN_NONE;
}

static PyObject *
OTF_clone(PyObject *self, PyObject *Py_UNUSED(args))
{
    UiOpenTypeFeaturesObject *o = (UiOpenTypeFeaturesObject *)self;
    UiOpenTypeFeaturesObject *clone = PyObject_GC_New(
        UiOpenTypeFeaturesObject, OpenTypeFeaturesType);
    if (clone == NULL) return NULL;
    clone->otf = uiOpenTypeFeaturesClone(o->otf);
    clone->owned = 1;
    PyObject_GC_Track((PyObject *)clone);
    return (PyObject *)clone;
}

/* ForEach callback for items() */
typedef struct {
    PyObject *list;
    int error;
} OTF_ForEach_Data;

static uiForEach
otf_foreach_cb(const uiOpenTypeFeatures *otf,
               char a, char b, char c, char d, uint32_t value, void *data)
{
    OTF_ForEach_Data *fed = (OTF_ForEach_Data *)data;
    if (fed->error) return uiForEachStop;

    char tag[5] = {a, b, c, d, '\0'};
    PyObject *tuple = Py_BuildValue("(sI)", tag, value);
    if (tuple == NULL) { fed->error = 1; return uiForEachStop; }
    if (PyList_Append(fed->list, tuple) < 0) {
        Py_DECREF(tuple);
        fed->error = 1;
        return uiForEachStop;
    }
    Py_DECREF(tuple);
    return uiForEachContinue;
}

static PyObject *
OTF_items(PyObject *self, PyObject *Py_UNUSED(args))
{
    UiOpenTypeFeaturesObject *o = (UiOpenTypeFeaturesObject *)self;
    OTF_ForEach_Data fed = { PyList_New(0), 0 };
    if (fed.list == NULL) return NULL;
    uiOpenTypeFeaturesForEach(o->otf, otf_foreach_cb, &fed);
    if (fed.error) {
        Py_DECREF(fed.list);
        return NULL;
    }
    return fed.list;
}

static int
OTF_traverse(PyObject *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static int
OTF_clear(PyObject *self)
{
    return 0;
}

static void
OTF_dealloc(PyObject *self)
{
    UiOpenTypeFeaturesObject *o = (UiOpenTypeFeaturesObject *)self;
    PyObject_GC_UnTrack(self);
    if (o->otf != NULL && o->owned) {
        uiFreeOpenTypeFeatures(o->otf);
        o->otf = NULL;
    }
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyMethodDef OTF_methods[] = {
    {"add",    OTF_add,    METH_VARARGS, "add(tag, value)\n--\n\nSet a 4-character OpenType feature tag."},
    {"remove", OTF_remove, METH_VARARGS, "remove(tag)\n--\n\nRemove an OpenType feature tag."},
    {"get",    OTF_get,    METH_VARARGS, "get(tag)\n--\n\nGet the value of an OpenType feature tag, or None."},
    {"clone",  OTF_clone,  METH_NOARGS,  "Return a copy of the features."},
    {"items",  OTF_items,  METH_NOARGS,  "Return a list of (tag, value) tuples."},
    {NULL}
};

static PyType_Slot OTF_slots[] = {
    {Py_tp_doc,       "OpenTypeFeatures()\n--\n\nA set of OpenType font feature tags."},
    {Py_tp_init,      OTF_init},
    {Py_tp_methods,   OTF_methods},
    {Py_tp_dealloc,   OTF_dealloc},
    {Py_tp_traverse,  OTF_traverse},
    {Py_tp_clear,     OTF_clear},
    {0, NULL}
};

PyType_Spec OpenTypeFeatures_spec = {
    .name      = "libui.core.OpenTypeFeatures",
    .basicsize = sizeof(UiOpenTypeFeaturesObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = OTF_slots,
};

/* -- Attribute ----------------------------------------------------- */

typedef struct {
    PyObject_HEAD
    uiAttribute *attr;
    int owned;  /* 0 if given to AttributedString */
} UiAttributeObject;

/* Helper: wrap a uiAttribute* into a Python Attribute.
 * The new object owns the attribute (owned=1). */
static PyObject *
wrap_attribute(uiAttribute *raw)
{
    if (raw == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "failed to create attribute");
        return NULL;
    }
    UiAttributeObject *a = PyObject_GC_New(UiAttributeObject, AttributeType);
    if (a == NULL) {
        uiFreeAttribute(raw);
        return NULL;
    }
    a->attr = raw;
    a->owned = 1;
    PyObject_GC_Track((PyObject *)a);
    return (PyObject *)a;
}

/* Read-only properties */
static PyObject *
Attr_get_type(PyObject *self, void *closure)
{
    UiAttributeObject *a = (UiAttributeObject *)self;
    return PyLong_FromLong(uiAttributeGetType(a->attr));
}

static PyObject *
Attr_get_family(PyObject *self, void *closure)
{
    UiAttributeObject *a = (UiAttributeObject *)self;
    if (uiAttributeGetType(a->attr) != uiAttributeTypeFamily) Py_RETURN_NONE;
    return PyUnicode_FromString(uiAttributeFamily(a->attr));
}

static PyObject *
Attr_get_size(PyObject *self, void *closure)
{
    UiAttributeObject *a = (UiAttributeObject *)self;
    if (uiAttributeGetType(a->attr) != uiAttributeTypeSize) Py_RETURN_NONE;
    return PyFloat_FromDouble(uiAttributeSize(a->attr));
}

static PyObject *
Attr_get_weight(PyObject *self, void *closure)
{
    UiAttributeObject *a = (UiAttributeObject *)self;
    if (uiAttributeGetType(a->attr) != uiAttributeTypeWeight) Py_RETURN_NONE;
    return PyLong_FromLong(uiAttributeWeight(a->attr));
}

static PyObject *
Attr_get_italic(PyObject *self, void *closure)
{
    UiAttributeObject *a = (UiAttributeObject *)self;
    if (uiAttributeGetType(a->attr) != uiAttributeTypeItalic) Py_RETURN_NONE;
    return PyLong_FromLong(uiAttributeItalic(a->attr));
}

static PyObject *
Attr_get_stretch(PyObject *self, void *closure)
{
    UiAttributeObject *a = (UiAttributeObject *)self;
    if (uiAttributeGetType(a->attr) != uiAttributeTypeStretch) Py_RETURN_NONE;
    return PyLong_FromLong(uiAttributeStretch(a->attr));
}

static PyObject *
Attr_get_color(PyObject *self, void *closure)
{
    UiAttributeObject *a = (UiAttributeObject *)self;
    uiAttributeType t = uiAttributeGetType(a->attr);
    if (t != uiAttributeTypeColor && t != uiAttributeTypeBackground)
        Py_RETURN_NONE;
    double r, g, b, al;
    uiAttributeColor(a->attr, &r, &g, &b, &al);
    return Py_BuildValue("(dddd)", r, g, b, al);
}

static PyObject *
Attr_get_underline(PyObject *self, void *closure)
{
    UiAttributeObject *a = (UiAttributeObject *)self;
    if (uiAttributeGetType(a->attr) != uiAttributeTypeUnderline) Py_RETURN_NONE;
    return PyLong_FromLong(uiAttributeUnderline(a->attr));
}

static PyObject *
Attr_get_underline_color(PyObject *self, void *closure)
{
    UiAttributeObject *a = (UiAttributeObject *)self;
    if (uiAttributeGetType(a->attr) != uiAttributeTypeUnderlineColor)
        Py_RETURN_NONE;
    uiUnderlineColor kind;
    double r, g, b, al;
    uiAttributeUnderlineColor(a->attr, &kind, &r, &g, &b, &al);
    return Py_BuildValue("(idddd)", (int)kind, r, g, b, al);
}

static PyObject *
Attr_get_features(PyObject *self, void *closure)
{
    UiAttributeObject *a = (UiAttributeObject *)self;
    if (uiAttributeGetType(a->attr) != uiAttributeTypeFeatures)
        Py_RETURN_NONE;
    const uiOpenTypeFeatures *otf = uiAttributeFeatures(a->attr);
    /* Return a clone so caller can freely modify it */
    UiOpenTypeFeaturesObject *clone = PyObject_GC_New(
        UiOpenTypeFeaturesObject, OpenTypeFeaturesType);
    if (clone == NULL) return NULL;
    clone->otf = uiOpenTypeFeaturesClone(otf);
    clone->owned = 1;
    PyObject_GC_Track((PyObject *)clone);
    return (PyObject *)clone;
}

static int
Attr_traverse(PyObject *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static int
Attr_clear(PyObject *self)
{
    return 0;
}

static void
Attr_dealloc(PyObject *self)
{
    UiAttributeObject *a = (UiAttributeObject *)self;
    PyObject_GC_UnTrack(self);
    if (a->attr != NULL && a->owned) {
        uiFreeAttribute(a->attr);
        a->attr = NULL;
    }
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyGetSetDef Attr_getset[] = {
    {"type",            Attr_get_type,            NULL, "Attribute type (AttributeKind enum).", NULL},
    {"family",          Attr_get_family,          NULL, "Font family name, or None.", NULL},
    {"size",            Attr_get_size,            NULL, "Font size, or None.", NULL},
    {"weight",          Attr_get_weight,          NULL, "Font weight (TextWeight), or None.", NULL},
    {"italic",          Attr_get_italic,          NULL, "Italic style (TextItalic), or None.", NULL},
    {"stretch",         Attr_get_stretch,         NULL, "Font stretch (TextStretch), or None.", NULL},
    {"color",           Attr_get_color,           NULL, "Color as (r, g, b, a), or None.", NULL},
    {"underline",       Attr_get_underline,       NULL, "Underline style (Underline), or None.", NULL},
    {"underline_color", Attr_get_underline_color, NULL, "Underline color as (kind, r, g, b, a), or None.", NULL},
    {"features",        Attr_get_features,        NULL, "OpenType features, or None.", NULL},
    {NULL}
};

static PyType_Slot Attr_slots[] = {
    {Py_tp_doc,       "A text attribute. Created by factory functions, not directly."},
    {Py_tp_getset,    Attr_getset},
    {Py_tp_dealloc,   Attr_dealloc},
    {Py_tp_traverse,  Attr_traverse},
    {Py_tp_clear,     Attr_clear},
    {0, NULL}
};

PyType_Spec Attribute_spec = {
    .name      = "libui.core.Attribute",
    .basicsize = sizeof(UiAttributeObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = Attr_slots,
};

/* -- Module-level Attribute factory functions ---------------------- */

PyObject *
mod_family_attribute(PyObject *Py_UNUSED(self), PyObject *args)
{
    const char *name;
    if (!PyArg_ParseTuple(args, "s", &name)) return NULL;
    return wrap_attribute(uiNewFamilyAttribute(name));
}

PyObject *
mod_size_attribute(PyObject *Py_UNUSED(self), PyObject *args)
{
    double size;
    if (!PyArg_ParseTuple(args, "d", &size)) return NULL;
    return wrap_attribute(uiNewSizeAttribute(size));
}

PyObject *
mod_weight_attribute(PyObject *Py_UNUSED(self), PyObject *args)
{
    int weight;
    if (!PyArg_ParseTuple(args, "i", &weight)) return NULL;
    return wrap_attribute(uiNewWeightAttribute((uiTextWeight)weight));
}

PyObject *
mod_italic_attribute(PyObject *Py_UNUSED(self), PyObject *args)
{
    int italic;
    if (!PyArg_ParseTuple(args, "i", &italic)) return NULL;
    return wrap_attribute(uiNewItalicAttribute((uiTextItalic)italic));
}

PyObject *
mod_stretch_attribute(PyObject *Py_UNUSED(self), PyObject *args)
{
    int stretch;
    if (!PyArg_ParseTuple(args, "i", &stretch)) return NULL;
    return wrap_attribute(uiNewStretchAttribute((uiTextStretch)stretch));
}

PyObject *
mod_color_attribute(PyObject *Py_UNUSED(self), PyObject *args)
{
    double r, g, b, a;
    if (!PyArg_ParseTuple(args, "dddd", &r, &g, &b, &a)) return NULL;
    return wrap_attribute(uiNewColorAttribute(r, g, b, a));
}

PyObject *
mod_background_attribute(PyObject *Py_UNUSED(self), PyObject *args)
{
    double r, g, b, a;
    if (!PyArg_ParseTuple(args, "dddd", &r, &g, &b, &a)) return NULL;
    return wrap_attribute(uiNewBackgroundAttribute(r, g, b, a));
}

PyObject *
mod_underline_attribute(PyObject *Py_UNUSED(self), PyObject *args)
{
    int underline;
    if (!PyArg_ParseTuple(args, "i", &underline)) return NULL;
    return wrap_attribute(uiNewUnderlineAttribute((uiUnderline)underline));
}

PyObject *
mod_underline_color_attribute(PyObject *Py_UNUSED(self), PyObject *args)
{
    int kind;
    double r, g, b, a;
    if (!PyArg_ParseTuple(args, "idddd", &kind, &r, &g, &b, &a)) return NULL;
    return wrap_attribute(uiNewUnderlineColorAttribute((uiUnderlineColor)kind, r, g, b, a));
}

PyObject *
mod_features_attribute(PyObject *Py_UNUSED(self), PyObject *args)
{
    PyObject *otf_obj;
    if (!PyArg_ParseTuple(args, "O!", OpenTypeFeaturesType, &otf_obj))
        return NULL;
    UiOpenTypeFeaturesObject *otf = (UiOpenTypeFeaturesObject *)otf_obj;
    /* libui copies the features, so we don't transfer ownership */
    return wrap_attribute(uiNewFeaturesAttribute(otf->otf));
}

/* -- Text attribute enums ------------------------------------------ */

static const EnumMember attribute_type_members[] = {
    {"FAMILY",          uiAttributeTypeFamily},
    {"SIZE",            uiAttributeTypeSize},
    {"WEIGHT",          uiAttributeTypeWeight},
    {"ITALIC",          uiAttributeTypeItalic},
    {"STRETCH",         uiAttributeTypeStretch},
    {"COLOR",           uiAttributeTypeColor},
    {"BACKGROUND",      uiAttributeTypeBackground},
    {"UNDERLINE",       uiAttributeTypeUnderline},
    {"UNDERLINE_COLOR", uiAttributeTypeUnderlineColor},
    {"FEATURES",        uiAttributeTypeFeatures},
};

static const EnumMember text_weight_members[] = {
    {"THIN",        uiTextWeightThin},
    {"ULTRA_LIGHT", uiTextWeightUltraLight},
    {"LIGHT",       uiTextWeightLight},
    {"BOOK",        uiTextWeightBook},
    {"NORMAL",      uiTextWeightNormal},
    {"MEDIUM",      uiTextWeightMedium},
    {"SEMI_BOLD",   uiTextWeightSemiBold},
    {"BOLD",        uiTextWeightBold},
    {"ULTRA_BOLD",  uiTextWeightUltraBold},
    {"HEAVY",       uiTextWeightHeavy},
    {"ULTRA_HEAVY", uiTextWeightUltraHeavy},
};

static const EnumMember text_italic_members[] = {
    {"NORMAL",  uiTextItalicNormal},
    {"OBLIQUE", uiTextItalicOblique},
    {"ITALIC",  uiTextItalicItalic},
};

static const EnumMember text_stretch_members[] = {
    {"ULTRA_CONDENSED", uiTextStretchUltraCondensed},
    {"EXTRA_CONDENSED", uiTextStretchExtraCondensed},
    {"CONDENSED",       uiTextStretchCondensed},
    {"SEMI_CONDENSED",  uiTextStretchSemiCondensed},
    {"NORMAL",          uiTextStretchNormal},
    {"SEMI_EXPANDED",   uiTextStretchSemiExpanded},
    {"EXPANDED",        uiTextStretchExpanded},
    {"EXTRA_EXPANDED",  uiTextStretchExtraExpanded},
    {"ULTRA_EXPANDED",  uiTextStretchUltraExpanded},
};

static const EnumMember underline_members[] = {
    {"NONE",       uiUnderlineNone},
    {"SINGLE",     uiUnderlineSingle},
    {"DOUBLE",     uiUnderlineDouble},
    {"SUGGESTION", uiUnderlineSuggestion},
};

static const EnumMember underline_color_members[] = {
    {"CUSTOM",    uiUnderlineColorCustom},
    {"SPELLING",  uiUnderlineColorSpelling},
    {"GRAMMAR",   uiUnderlineColorGrammar},
    {"AUXILIARY",  uiUnderlineColorAuxiliary},
};

int
register_attribute_enums(PyObject *module, PyObject *IntEnum)
{
    if (add_enum(module, IntEnum, "AttributeKind",
                 attribute_type_members, N_MEMBERS(attribute_type_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "TextWeight",
                 text_weight_members, N_MEMBERS(text_weight_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "TextItalic",
                 text_italic_members, N_MEMBERS(text_italic_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "TextStretch",
                 text_stretch_members, N_MEMBERS(text_stretch_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "Underline",
                 underline_members, N_MEMBERS(underline_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "UnderlineColor",
                 underline_color_members, N_MEMBERS(underline_color_members)) < 0) return -1;
    return 0;
}
