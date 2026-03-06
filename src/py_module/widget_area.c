/*
 * widget_area.c — Area and ScrollingArea types.
 *
 * These are Control subclasses with custom handler trampolines.
 */
#include "module.h"

/* Forward declare DrawContext struct for wrapping */
typedef struct {
    PyObject_HEAD
    uiDrawContext *ctx;
    int valid;
} UiDrawContextObject;

/* Handler data — embedded handler + back-ref to Python object */
typedef struct {
    uiAreaHandler handler;  /* must be first */
    PyObject *self;         /* back-ref to Python Area object */
} AreaHandlerData;

/* -- Trampolines --------------------------------------------------- */

static void
area_draw_trampoline(uiAreaHandler *ah, uiArea *area, uiAreaDrawParams *params)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    AreaHandlerData *data = (AreaHandlerData *)ah;
    UiControlObject *self = as_ctrl(data->self);

    PyObject *cb = PyDict_GetItemString(self->callbacks, "on_draw");
    if (cb == NULL || cb == Py_None) {
        PyGILState_Release(gstate);
        return;
    }

    /* Create a transient DrawContext */
    UiDrawContextObject *ctx_obj = PyObject_GC_New(
        UiDrawContextObject, DrawContextType);
    if (ctx_obj == NULL) {
        PyErr_WriteUnraisable(cb);
        PyGILState_Release(gstate);
        return;
    }
    ctx_obj->ctx = params->Context;
    ctx_obj->valid = 1;
    PyObject_GC_Track((PyObject *)ctx_obj);

    PyObject *result = PyObject_CallFunction(cb, "Odddddd",
        ctx_obj,
        params->AreaWidth, params->AreaHeight,
        params->ClipX, params->ClipY,
        params->ClipWidth, params->ClipHeight);

    ctx_obj->valid = 0;  /* Invalidate after callback */
    Py_DECREF(ctx_obj);

    if (result == NULL)
        PyErr_WriteUnraisable(cb);
    else
        Py_DECREF(result);

    PyGILState_Release(gstate);
}

static void
area_mouse_event_trampoline(uiAreaHandler *ah, uiArea *area, uiAreaMouseEvent *e)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    AreaHandlerData *data = (AreaHandlerData *)ah;
    UiControlObject *self = as_ctrl(data->self);

    PyObject *cb = PyDict_GetItemString(self->callbacks, "on_mouse_event");
    if (cb == NULL || cb == Py_None) {
        PyGILState_Release(gstate);
        return;
    }

    PyObject *dict = Py_BuildValue(
        "{s:d, s:d, s:d, s:d, s:i, s:i, s:i, s:i, s:K}",
        "x", e->X, "y", e->Y,
        "area_width", e->AreaWidth, "area_height", e->AreaHeight,
        "down", e->Down, "up", e->Up, "count", e->Count,
        "modifiers", (int)e->Modifiers, "held", (unsigned long long)e->Held1To64);

    if (dict == NULL) {
        PyErr_WriteUnraisable(cb);
        PyGILState_Release(gstate);
        return;
    }

    PyObject *result = PyObject_CallFunctionObjArgs(cb, dict, NULL);
    Py_DECREF(dict);
    if (result == NULL)
        PyErr_WriteUnraisable(cb);
    else
        Py_DECREF(result);

    PyGILState_Release(gstate);
}

static void
area_mouse_crossed_trampoline(uiAreaHandler *ah, uiArea *area, int left)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    AreaHandlerData *data = (AreaHandlerData *)ah;
    UiControlObject *self = as_ctrl(data->self);

    PyObject *cb = PyDict_GetItemString(self->callbacks, "on_mouse_crossed");
    if (cb == NULL || cb == Py_None) {
        PyGILState_Release(gstate);
        return;
    }

    PyObject *result = PyObject_CallFunction(cb, "O", left ? Py_True : Py_False);
    if (result == NULL)
        PyErr_WriteUnraisable(cb);
    else
        Py_DECREF(result);

    PyGILState_Release(gstate);
}

static void
area_drag_broken_trampoline(uiAreaHandler *ah, uiArea *area)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    AreaHandlerData *data = (AreaHandlerData *)ah;
    UiControlObject *self = as_ctrl(data->self);

    PyObject *cb = PyDict_GetItemString(self->callbacks, "on_drag_broken");
    if (cb == NULL || cb == Py_None) {
        PyGILState_Release(gstate);
        return;
    }

    PyObject *result = PyObject_CallNoArgs(cb);
    if (result == NULL)
        PyErr_WriteUnraisable(cb);
    else
        Py_DECREF(result);

    PyGILState_Release(gstate);
}

static int
area_key_event_trampoline(uiAreaHandler *ah, uiArea *area, uiAreaKeyEvent *e)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    AreaHandlerData *data = (AreaHandlerData *)ah;
    UiControlObject *self = as_ctrl(data->self);

    PyObject *cb = PyDict_GetItemString(self->callbacks, "on_key_event");
    if (cb == NULL || cb == Py_None) {
        PyGILState_Release(gstate);
        return 0;
    }

    char key_str[2] = {e->Key, '\0'};
    PyObject *dict = Py_BuildValue(
        "{s:s, s:i, s:i, s:i, s:i}",
        "key", key_str,
        "ext_key", (int)e->ExtKey,
        "modifier", (int)e->Modifier,
        "modifiers", (int)e->Modifiers,
        "up", e->Up);

    if (dict == NULL) {
        PyErr_WriteUnraisable(cb);
        PyGILState_Release(gstate);
        return 0;
    }

    PyObject *result = PyObject_CallFunctionObjArgs(cb, dict, NULL);
    Py_DECREF(dict);

    int ret = 0;
    if (result == NULL) {
        PyErr_WriteUnraisable(cb);
    } else {
        ret = PyObject_IsTrue(result);
        Py_DECREF(result);
    }

    PyGILState_Release(gstate);
    return ret;
}

/* -- PyCapsule destructor for handler data -------------------------- */

static void
handler_capsule_destructor(PyObject *capsule)
{
    AreaHandlerData *hd = (AreaHandlerData *)PyCapsule_GetPointer(capsule, NULL);
    if (hd != NULL) PyMem_Free(hd);
}

/* -- Area_init ----------------------------------------------------- */

static int
Area_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"on_draw", "on_mouse_event", "on_mouse_crossed",
                             "on_drag_broken", "on_key_event", NULL};
    PyObject *on_draw, *on_mouse = Py_None, *on_crossed = Py_None;
    PyObject *on_drag = Py_None, *on_key = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|OOOO", kwlist,
                                     &on_draw, &on_mouse, &on_crossed,
                                     &on_drag, &on_key))
        return -1;

    if (!PyCallable_Check(on_draw)) {
        PyErr_SetString(PyExc_TypeError, "on_draw must be callable");
        return -1;
    }

    /* Allocate handler data */
    AreaHandlerData *hd = PyMem_Malloc(sizeof(AreaHandlerData));
    if (hd == NULL) { PyErr_NoMemory(); return -1; }

    hd->handler.Draw = area_draw_trampoline;
    hd->handler.MouseEvent = area_mouse_event_trampoline;
    hd->handler.MouseCrossed = area_mouse_crossed_trampoline;
    hd->handler.DragBroken = area_drag_broken_trampoline;
    hd->handler.KeyEvent = area_key_event_trampoline;
    hd->self = self;  /* back-ref (borrowed — Area outlives handler) */

    uiArea *a = uiNewArea(&hd->handler);
    if (init_base(as_ctrl(self), uiControl(a)) < 0) {
        PyMem_Free(hd);
        return -1;
    }

    /* Store callbacks */
    store_callback(as_ctrl(self), "on_draw", on_draw);
    if (on_mouse != Py_None)
        store_callback(as_ctrl(self), "on_mouse_event", on_mouse);
    if (on_crossed != Py_None)
        store_callback(as_ctrl(self), "on_mouse_crossed", on_crossed);
    if (on_drag != Py_None)
        store_callback(as_ctrl(self), "on_drag_broken", on_drag);
    if (on_key != Py_None)
        store_callback(as_ctrl(self), "on_key_event", on_key);

    /* Store handler data as PyCapsule to prevent leak (bypass store_callback
     * since PyCapsules are not callable) */
    PyObject *capsule = PyCapsule_New(hd, NULL, handler_capsule_destructor);
    if (capsule == NULL) { PyMem_Free(hd); return -1; }
    PyObject *key = PyUnicode_FromString("_handler");
    PyDict_SetItem(as_ctrl(self)->callbacks, key, capsule);
    Py_DECREF(key);
    Py_DECREF(capsule);

    return 0;
}

/* -- Area methods -------------------------------------------------- */

static PyObject *
Area_queue_redraw_all(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiAreaQueueRedrawAll(uiArea(as_ctrl(self)->control));
    Py_RETURN_NONE;
}

static PyObject *
Area_scroll_to(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double x, y, w, h;
    if (!PyArg_ParseTuple(args, "dddd", &x, &y, &w, &h)) return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    if (!PyObject_IsInstance(self, (PyObject *)ScrollingAreaType)) {
        PyErr_SetString(PyExc_RuntimeError,
            "scroll_to() can only be called on a ScrollingArea");
        return NULL;
    }
    uiAreaScrollTo(uiArea(as_ctrl(self)->control), x, y, w, h);
    Py_RETURN_NONE;
}

static PyObject *
Area_set_size(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    int w, h;
    if (!PyArg_ParseTuple(args, "ii", &w, &h)) return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    if (!PyObject_IsInstance(self, (PyObject *)ScrollingAreaType)) {
        PyErr_SetString(PyExc_RuntimeError,
            "set_size() can only be called on a ScrollingArea");
        return NULL;
    }
    uiAreaSetSize(uiArea(as_ctrl(self)->control), w, h);
    Py_RETURN_NONE;
}

static PyObject *
Area_begin_user_window_move(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiAreaBeginUserWindowMove(uiArea(as_ctrl(self)->control));
    Py_RETURN_NONE;
}

static PyObject *
Area_begin_user_window_resize(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    int edge;
    if (!PyArg_ParseTuple(args, "i", &edge)) return NULL;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiAreaBeginUserWindowResize(uiArea(as_ctrl(self)->control),
                                (uiWindowResizeEdge)edge);
    Py_RETURN_NONE;
}

static PyMethodDef Area_methods[] = {
    {"queue_redraw_all",           Area_queue_redraw_all,           METH_NOARGS,  "Request a full redraw."},
    {"scroll_to",                  Area_scroll_to,                  METH_VARARGS, "scroll_to(x, y, width, height)\n--\n\nScroll the area to show the given rectangle."},
    {"set_size",                   Area_set_size,                   METH_VARARGS, "set_size(width, height)\n--\n\nSet the scrollable area size."},
    {"begin_user_window_move",     Area_begin_user_window_move,     METH_NOARGS,  "Begin a user-initiated window move."},
    {"begin_user_window_resize",   Area_begin_user_window_resize,   METH_VARARGS, "begin_user_window_resize(edge)\n--\n\nBegin a user-initiated window resize."},
    {NULL}
};

static PyType_Slot Area_slots[] = {
    {Py_tp_doc,       "Area(on_draw, on_mouse_event=None, on_mouse_crossed=None, on_drag_broken=None, on_key_event=None)\n--\n\nA canvas for custom drawing."},
    {Py_tp_init,      Area_init},
    {Py_tp_methods,   Area_methods},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec Area_spec = {
    .name      = "libui.core.Area",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Area_slots,
};

/* -- ScrollingArea ------------------------------------------------- */

static int
ScrollingArea_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"on_draw", "width", "height",
                             "on_mouse_event", "on_mouse_crossed",
                             "on_drag_broken", "on_key_event", NULL};
    PyObject *on_draw, *on_mouse = Py_None, *on_crossed = Py_None;
    PyObject *on_drag = Py_None, *on_key = Py_None;
    int width, height;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "Oii|OOOO", kwlist,
                                     &on_draw, &width, &height,
                                     &on_mouse, &on_crossed,
                                     &on_drag, &on_key))
        return -1;

    if (!PyCallable_Check(on_draw)) {
        PyErr_SetString(PyExc_TypeError, "on_draw must be callable");
        return -1;
    }

    AreaHandlerData *hd = PyMem_Malloc(sizeof(AreaHandlerData));
    if (hd == NULL) { PyErr_NoMemory(); return -1; }

    hd->handler.Draw = area_draw_trampoline;
    hd->handler.MouseEvent = area_mouse_event_trampoline;
    hd->handler.MouseCrossed = area_mouse_crossed_trampoline;
    hd->handler.DragBroken = area_drag_broken_trampoline;
    hd->handler.KeyEvent = area_key_event_trampoline;
    hd->self = self;

    uiArea *a = uiNewScrollingArea(&hd->handler, width, height);
    if (init_base(as_ctrl(self), uiControl(a)) < 0) {
        PyMem_Free(hd);
        return -1;
    }

    store_callback(as_ctrl(self), "on_draw", on_draw);
    if (on_mouse != Py_None)
        store_callback(as_ctrl(self), "on_mouse_event", on_mouse);
    if (on_crossed != Py_None)
        store_callback(as_ctrl(self), "on_mouse_crossed", on_crossed);
    if (on_drag != Py_None)
        store_callback(as_ctrl(self), "on_drag_broken", on_drag);
    if (on_key != Py_None)
        store_callback(as_ctrl(self), "on_key_event", on_key);

    PyObject *capsule = PyCapsule_New(hd, NULL, handler_capsule_destructor);
    if (capsule == NULL) { PyMem_Free(hd); return -1; }
    PyObject *key = PyUnicode_FromString("_handler");
    PyDict_SetItem(as_ctrl(self)->callbacks, key, capsule);
    Py_DECREF(key);
    Py_DECREF(capsule);

    return 0;
}

static PyType_Slot ScrollingArea_slots[] = {
    {Py_tp_doc,       "ScrollingArea(on_draw, width, height, ...)\n--\n\nA scrollable canvas for custom drawing."},
    {Py_tp_init,      ScrollingArea_init},
    {Py_tp_dealloc,   Control_dealloc},
    {Py_tp_traverse,  Control_traverse},
    {Py_tp_clear,     Control_clear},
    {0, NULL}
};

PyType_Spec ScrollingArea_spec = {
    .name      = "libui.core.ScrollingArea",
    .basicsize = 0,
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = ScrollingArea_slots,
};

/* -- Input enums --------------------------------------------------- */

static const EnumMember modifier_members[] = {
    {"CTRL",  uiModifierCtrl},
    {"ALT",   uiModifierAlt},
    {"SHIFT", uiModifierShift},
    {"SUPER", uiModifierSuper},
};

static const EnumMember ext_key_members[] = {
    {"ESCAPE",     uiExtKeyEscape},
    {"INSERT",     uiExtKeyInsert},
    {"DELETE",     uiExtKeyDelete},
    {"HOME",       uiExtKeyHome},
    {"END",        uiExtKeyEnd},
    {"PAGE_UP",    uiExtKeyPageUp},
    {"PAGE_DOWN",  uiExtKeyPageDown},
    {"UP",         uiExtKeyUp},
    {"DOWN",       uiExtKeyDown},
    {"LEFT",       uiExtKeyLeft},
    {"RIGHT",      uiExtKeyRight},
    {"F1",         uiExtKeyF1},
    {"F2",         uiExtKeyF2},
    {"F3",         uiExtKeyF3},
    {"F4",         uiExtKeyF4},
    {"F5",         uiExtKeyF5},
    {"F6",         uiExtKeyF6},
    {"F7",         uiExtKeyF7},
    {"F8",         uiExtKeyF8},
    {"F9",         uiExtKeyF9},
    {"F10",        uiExtKeyF10},
    {"F11",        uiExtKeyF11},
    {"F12",        uiExtKeyF12},
    {"N0",         uiExtKeyN0},
    {"N1",         uiExtKeyN1},
    {"N2",         uiExtKeyN2},
    {"N3",         uiExtKeyN3},
    {"N4",         uiExtKeyN4},
    {"N5",         uiExtKeyN5},
    {"N6",         uiExtKeyN6},
    {"N7",         uiExtKeyN7},
    {"N8",         uiExtKeyN8},
    {"N9",         uiExtKeyN9},
    {"N_DOT",      uiExtKeyNDot},
    {"N_ENTER",    uiExtKeyNEnter},
    {"N_ADD",      uiExtKeyNAdd},
    {"N_SUBTRACT", uiExtKeyNSubtract},
    {"N_MULTIPLY", uiExtKeyNMultiply},
    {"N_DIVIDE",   uiExtKeyNDivide},
};

static const EnumMember window_resize_edge_members[] = {
    {"LEFT",         uiWindowResizeEdgeLeft},
    {"TOP",          uiWindowResizeEdgeTop},
    {"RIGHT",        uiWindowResizeEdgeRight},
    {"BOTTOM",       uiWindowResizeEdgeBottom},
    {"TOP_LEFT",     uiWindowResizeEdgeTopLeft},
    {"TOP_RIGHT",    uiWindowResizeEdgeTopRight},
    {"BOTTOM_LEFT",  uiWindowResizeEdgeBottomLeft},
    {"BOTTOM_RIGHT", uiWindowResizeEdgeBottomRight},
};

int
register_area_enums(PyObject *module, PyObject *IntEnum, PyObject *IntFlag)
{
    if (add_enum(module, IntFlag, "Modifier",
                 modifier_members, N_MEMBERS(modifier_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "ExtKey",
                 ext_key_members, N_MEMBERS(ext_key_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "WindowResizeEdge",
                 window_resize_edge_members, N_MEMBERS(window_resize_edge_members)) < 0) return -1;
    return 0;
}
