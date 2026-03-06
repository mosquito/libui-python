/*
 * _core_control.c — Control base type, helpers, callback trampolines.
 */
#include "module.h"

/* -- Global tracking list ------------------------------------------ */

/*
 * Sentinel node for intrusive doubly-linked list of all live controls.
 * Only the track_prev/track_next fields are used; the rest is zeroed.
 */
static UiControlObject track_sentinel;
static int track_initialized = 0;

static void
ensure_track_init(void)
{
    if (!track_initialized) {
        track_sentinel.track_prev = &track_sentinel;
        track_sentinel.track_next = &track_sentinel;
        track_initialized = 1;
    }
}

void
track_control(UiControlObject *c)
{
    ensure_track_init();
    c->track_next = track_sentinel.track_next;
    c->track_prev = &track_sentinel;
    track_sentinel.track_next->track_prev = c;
    track_sentinel.track_next = c;
}

void
untrack_control(UiControlObject *c)
{
    if (c->track_prev != NULL) {
        c->track_prev->track_next = c->track_next;
        c->track_next->track_prev = c->track_prev;
        c->track_prev = NULL;
        c->track_next = NULL;
    }
}

void
uninit_all_controls(void)
{
    /*
     * Destroy all owned top-level (unparented) controls, then invalidate
     * all remaining tracked controls.  Must be called BEFORE uiUninit()
     * so libui doesn't abort on leaked allocations.
     */
    ensure_track_init();

    /* Walk the list.  For each owned control, save the C pointer,
     * invalidate the whole Python tree (sets control=NULL), then destroy
     * the C control.  Restart after each destroy because invalidation
     * can change control states of other tracked nodes. */
    int found = 1;
    while (found) {
        found = 0;
        for (UiControlObject *c = track_sentinel.track_next;
             c != &track_sentinel; c = c->track_next) {
            if (c->control != NULL && c->owned) {
                uiControl *ctrl = c->control;
                invalidate_control_tree(c);
                uiControlDestroy(ctrl);
                found = 1;
                break;
            }
        }
    }

    /* Safety net: invalidate any remaining tracked controls */
    for (UiControlObject *c = track_sentinel.track_next;
         c != &track_sentinel; c = c->track_next) {
        c->control = NULL;
        c->owned = 0;
    }
}

/* -- Resource tracking (non-Control libui objects) ------------------ */

static UiResourceNode res_sentinel;
static int res_initialized = 0;

static void
ensure_res_init(void)
{
    if (!res_initialized) {
        res_sentinel.res_prev = &res_sentinel;
        res_sentinel.res_next = &res_sentinel;
        res_initialized = 1;
    }
}

void
track_resource(UiResourceNode *node, void **handle_ptr, resource_free_fn free_fn)
{
    ensure_res_init();
    node->handle_ptr = handle_ptr;
    node->free_fn = free_fn;
    node->res_next = res_sentinel.res_next;
    node->res_prev = &res_sentinel;
    res_sentinel.res_next->res_prev = node;
    res_sentinel.res_next = node;
}

void
untrack_resource(UiResourceNode *node)
{
    if (node->res_prev != NULL) {
        node->res_prev->res_next = node->res_next;
        node->res_next->res_prev = node->res_prev;
        node->res_prev = NULL;
        node->res_next = NULL;
    }
}

void
uninit_all_resources(void)
{
    ensure_res_init();
    for (UiResourceNode *n = res_sentinel.res_next;
         n != &res_sentinel; n = n->res_next) {
        if (n->handle_ptr != NULL && *n->handle_ptr != NULL) {
            n->free_fn(*n->handle_ptr);
            *n->handle_ptr = NULL;
        }
    }
}

/* -- check_control ------------------------------------------------- */

int
check_control(UiControlObject *self)
{
    if (self->control == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "control has been destroyed");
        return -1;
    }
    return 0;
}

/* -- init_base ----------------------------------------------------- */

int
init_base(UiControlObject *self, uiControl *ctrl)
{
    self->control = ctrl;
    self->owned = 1;
    self->children = PyList_New(0);
    if (self->children == NULL) return -1;
    self->callbacks = PyDict_New();
    if (self->callbacks == NULL) return -1;
    track_control(self);
    return 0;
}

/* -- store_callback ------------------------------------------------ */

int
store_callback(UiControlObject *self, const char *key, PyObject *callable)
{
    if (!PyCallable_Check(callable)) {
        PyErr_SetString(PyExc_TypeError, "callback must be callable");
        return -1;
    }
    PyObject *pykey = PyUnicode_FromString(key);
    if (pykey == NULL) return -1;
    int rc = PyDict_SetItem(self->callbacks, pykey, callable);
    Py_DECREF(pykey);
    return rc;
}

/* -- Async coroutine scheduling helper ----------------------------- */

void
schedule_coroutine_threadsafe(PyObject *coro, PyObject *callable)
{
    /*
     * Schedule a coroutine on the asyncio loop running in the background
     * thread.  Uses call_soon_threadsafe(loop.create_task, coro) so it is
     * safe to call from the main (UI) thread where trampolines fire.
     */
    if (g_asyncio_loop == NULL) {
        /* No loop registered — close the unawaited coroutine */
        PyObject *cr = PyObject_CallMethod(coro, "close", NULL);
        Py_XDECREF(cr);
        return;
    }
    PyObject *create_task = PyObject_GetAttrString(g_asyncio_loop, "create_task");
    if (create_task == NULL) {
        PyErr_WriteUnraisable(callable);
        return;
    }
    PyObject *rv = PyObject_CallMethod(
        g_asyncio_loop, "call_soon_threadsafe", "OO", create_task, coro);
    if (rv == NULL)
        PyErr_WriteUnraisable(callable);
    Py_XDECREF(rv);
    Py_DECREF(create_task);
}

static void
maybe_schedule_coroutine(PyObject *result, PyObject *callable)
{
    if (!PyCoro_CheckExact(result))
        return;
    schedule_coroutine_threadsafe(result, callable);
}

/* -- Trampolines --------------------------------------------------- */

void
trampoline_void(void *sender, void *data)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *callable = (PyObject *)data;
    PyObject *result = PyObject_CallNoArgs(callable);
    if (result == NULL) {
        PyErr_WriteUnraisable(callable);
    } else {
        maybe_schedule_coroutine(result, callable);
        Py_DECREF(result);
    }
    PyGILState_Release(gstate);
}

int
trampoline_int_return(void *sender, void *data)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *callable = (PyObject *)data;
    PyObject *result = PyObject_CallNoArgs(callable);
    int ret = 0;
    if (result == NULL) {
        PyErr_WriteUnraisable(callable);
    } else if (PyCoro_CheckExact(result)) {
        maybe_schedule_coroutine(result, callable);
        Py_DECREF(result);
    } else {
        ret = PyObject_IsTrue(result);
        Py_DECREF(result);
    }
    PyGILState_Release(gstate);
    return ret;
}

int
trampoline_should_quit(void *data)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *callable = (PyObject *)data;
    PyObject *result = PyObject_CallNoArgs(callable);
    int ret = 0;
    if (result == NULL) {
        PyErr_WriteUnraisable(callable);
    } else {
        ret = PyObject_IsTrue(result);
        Py_DECREF(result);
    }
    PyGILState_Release(gstate);
    return ret;
}

/* -- Invalidation helper ------------------------------------------- */

void
invalidate_control_tree(UiControlObject *c)
{
    /* Mark this control as no longer valid — libui has already destroyed it */
    c->control = NULL;
    c->owned = 0;

    /* Recursively invalidate children */
    if (c->children != NULL) {
        Py_ssize_t n = PyList_Size(c->children);
        for (Py_ssize_t i = 0; i < n; i++) {
            PyObject *child = PyList_GetItem(c->children, i);
            if (child != NULL && PyObject_TypeCheck(child, ControlType))
                invalidate_control_tree(as_ctrl(child));
        }
    }
}

/* -- GC support ---------------------------------------------------- */

int
Control_traverse(PyObject *self, visitproc visit, void *arg)
{
    UiControlObject *c = as_ctrl(self);
    Py_VISIT(c->children);
    Py_VISIT(c->callbacks);
    Py_VISIT(Py_TYPE(self));
    return 0;
}

int
Control_clear(PyObject *self)
{
    UiControlObject *c = as_ctrl(self);
    Py_CLEAR(c->children);
    Py_CLEAR(c->callbacks);
    return 0;
}

void
Control_dealloc(PyObject *self)
{
    UiControlObject *c = as_ctrl(self);
    PyObject_GC_UnTrack(self);
    untrack_control(c);
    if (c->control != NULL && c->owned) {
        /* Invalidate children first — uiControlDestroy destroys them
         * at the C level, so their Python dealloc must not re-destroy. */
        if (c->children != NULL) {
            Py_ssize_t n = PyList_Size(c->children);
            for (Py_ssize_t i = 0; i < n; i++) {
                PyObject *child = PyList_GetItem(c->children, i);
                if (child != NULL && PyObject_TypeCheck(child, ControlType))
                    invalidate_control_tree(as_ctrl(child));
            }
        }
        uiControlDestroy(c->control);
        c->control = NULL;
    }
    Control_clear(self);
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

/* -- Control methods ----------------------------------------------- */

static PyObject *
Control_show(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiControlShow(as_ctrl(self)->control);
    Py_RETURN_NONE;
}

static PyObject *
Control_hide(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiControlHide(as_ctrl(self)->control);
    Py_RETURN_NONE;
}

static PyObject *
Control_enable(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiControlEnable(as_ctrl(self)->control);
    Py_RETURN_NONE;
}

static PyObject *
Control_disable(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    uiControlDisable(as_ctrl(self)->control);
    Py_RETURN_NONE;
}

static PyObject *
Control_destroy(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    UiControlObject *c = as_ctrl(self);
    if (c->control != NULL) {
        /* Invalidate children before destroying — libui will
         * recursively destroy them at the C level. */
        if (c->children != NULL) {
            Py_ssize_t n = PyList_Size(c->children);
            for (Py_ssize_t i = 0; i < n; i++) {
                PyObject *child = PyList_GetItem(c->children, i);
                if (child != NULL && PyObject_TypeCheck(child, ControlType))
                    invalidate_control_tree(as_ctrl(child));
            }
        }
        uiControlDestroy(c->control);
        c->control = NULL;
        c->owned = 0;
    }
    Py_RETURN_NONE;
}

static PyObject *
Control_get_visible(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiControlVisible(as_ctrl(self)->control));
}

static PyObject *
Control_get_enabled(PyObject *self, void *Py_UNUSED(closure))
{
    ENSURE_MAIN_THREAD;
    if (check_control(as_ctrl(self)) < 0) return NULL;
    return PyBool_FromLong(uiControlEnabled(as_ctrl(self)->control));
}

/* -- Control type definition --------------------------------------- */

static PyMethodDef Control_methods[] = {
    {"show",    Control_show,    METH_NOARGS, "Show the control."},
    {"hide",    Control_hide,    METH_NOARGS, "Hide the control."},
    {"enable",  Control_enable,  METH_NOARGS, "Enable the control."},
    {"disable", Control_disable, METH_NOARGS, "Disable the control."},
    {"destroy", Control_destroy, METH_NOARGS, "Destroy the underlying control."},
    {NULL}
};

static PyGetSetDef Control_getset[] = {
    {"visible", Control_get_visible, NULL, "True if the control is visible.", NULL},
    {"enabled", Control_get_enabled, NULL, "True if the control is enabled.", NULL},
    {NULL}
};

static PyType_Slot Control_slots[] = {
    {Py_tp_doc,      "Base class for all UI controls."},
    {Py_tp_methods,  Control_methods},
    {Py_tp_getset,   Control_getset},
    {Py_tp_dealloc,  Control_dealloc},
    {Py_tp_traverse, Control_traverse},
    {Py_tp_clear,    Control_clear},
    {0, NULL}
};

PyType_Spec Control_spec = {
    .name      = "libui.core.Control",
    .basicsize = sizeof(UiControlObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .slots     = Control_slots,
};
