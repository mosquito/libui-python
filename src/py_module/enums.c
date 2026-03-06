/*
 * enums.c — Shared add_enum() helper + general-purpose enums (Align, At).
 */
#include "module.h"

/* -- Shared helper: create IntEnum/IntFlag class on module ---------- */

int
add_enum(PyObject *module, PyObject *base,
         const char *cls_name,
         const EnumMember *members, int count)
{
    PyObject *dict = PyDict_New();
    if (!dict) return -1;
    for (int i = 0; i < count; i++) {
        PyObject *v = PyLong_FromLong(members[i].value);
        if (!v) { Py_DECREF(dict); return -1; }
        if (PyDict_SetItemString(dict, members[i].name, v) < 0) {
            Py_DECREF(v); Py_DECREF(dict); return -1;
        }
        Py_DECREF(v);
    }
    PyObject *cls = PyObject_CallFunction(base, "sO", cls_name, dict);
    Py_DECREF(dict);
    if (!cls) return -1;
    if (PyModule_AddObjectRef(module, cls_name, cls) < 0) {
        Py_DECREF(cls); return -1;
    }
    Py_DECREF(cls);
    return 0;
}

/* -- Grid enums ---------------------------------------------------- */

static const EnumMember align_members[] = {
    {"FILL",   uiAlignFill},
    {"START",  uiAlignStart},
    {"CENTER", uiAlignCenter},
    {"END",    uiAlignEnd},
};

static const EnumMember at_members[] = {
    {"LEADING",  uiAtLeading},
    {"TOP",      uiAtTop},
    {"TRAILING", uiAtTrailing},
    {"BOTTOM",   uiAtBottom},
};

int
register_grid_enums(PyObject *module, PyObject *IntEnum)
{
    if (add_enum(module, IntEnum, "Align",
                 align_members, N_MEMBERS(align_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "At",
                 at_members, N_MEMBERS(at_members)) < 0) return -1;
    return 0;
}
