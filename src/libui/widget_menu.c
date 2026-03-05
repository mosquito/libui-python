/* widget_menu.c — Menu and MenuItem types.
 *
 * These are NOT uiControl subclasses — they use custom structs.
 * Menu must be created before any Window.
 */
#include "module.h"

/* -- MenuItem ------------------------------------------------------ */

typedef struct {
    PyObject_HEAD
    uiMenuItem *item;
    PyObject *callback;   /* strong ref to on_clicked callable */
} UiMenuItemObject;

static void
menuitem_trampoline(uiMenuItem *sender, uiWindow *window, void *data)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *callable = (PyObject *)data;
    PyObject *result = PyObject_CallNoArgs(callable);
    if (result == NULL) {
        PyErr_WriteUnraisable(callable);
    } else {
        /* Support async callbacks */
        if (PyCoro_CheckExact(result)) {
            schedule_coroutine_threadsafe(result, callable);
        }
        Py_DECREF(result);
    }
    PyGILState_Release(gstate);
}

static PyObject *
MenuItem_enable(PyObject *self, PyObject *Py_UNUSED(args))
{
    UiMenuItemObject *mi = (UiMenuItemObject *)self;
    if (mi->item == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "menu item is invalid");
        return NULL;
    }
    uiMenuItemEnable(mi->item);
    Py_RETURN_NONE;
}

static PyObject *
MenuItem_disable(PyObject *self, PyObject *Py_UNUSED(args))
{
    UiMenuItemObject *mi = (UiMenuItemObject *)self;
    if (mi->item == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "menu item is invalid");
        return NULL;
    }
    uiMenuItemDisable(mi->item);
    Py_RETURN_NONE;
}

static PyObject *
MenuItem_get_checked(PyObject *self, void *Py_UNUSED(closure))
{
    UiMenuItemObject *mi = (UiMenuItemObject *)self;
    if (mi->item == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "menu item is invalid");
        return NULL;
    }
    return PyBool_FromLong(uiMenuItemChecked(mi->item));
}

static int
MenuItem_set_checked(PyObject *self, PyObject *value, void *Py_UNUSED(closure))
{
    UiMenuItemObject *mi = (UiMenuItemObject *)self;
    if (mi->item == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "menu item is invalid");
        return -1;
    }
    uiMenuItemSetChecked(mi->item, PyObject_IsTrue(value));
    return 0;
}

static PyObject *
MenuItem_on_clicked(PyObject *self, PyObject *args)
{
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    if (!PyCallable_Check(callable)) {
        PyErr_SetString(PyExc_TypeError, "callback must be callable");
        return NULL;
    }
    UiMenuItemObject *mi = (UiMenuItemObject *)self;
    if (mi->item == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "menu item is invalid");
        return NULL;
    }

    Py_XDECREF(mi->callback);
    Py_INCREF(callable);
    mi->callback = callable;

    uiMenuItemOnClicked(mi->item, menuitem_trampoline, callable);
    Py_RETURN_NONE;
}

static int
MenuItem_traverse(PyObject *self, visitproc visit, void *arg)
{
    UiMenuItemObject *mi = (UiMenuItemObject *)self;
    Py_VISIT(mi->callback);
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static int
MenuItem_clear(PyObject *self)
{
    UiMenuItemObject *mi = (UiMenuItemObject *)self;
    Py_CLEAR(mi->callback);
    return 0;
}

static void
MenuItem_dealloc(PyObject *self)
{
    PyObject_GC_UnTrack(self);
    MenuItem_clear(self);
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyMethodDef MenuItem_methods[] = {
    {"enable",     MenuItem_enable,     METH_NOARGS,
     "Enable the menu item."},
    {"disable",    MenuItem_disable,    METH_NOARGS,
     "Disable the menu item."},
    {"on_clicked", MenuItem_on_clicked, METH_VARARGS,
     "Register a callback for when the item is clicked."},
    {NULL}
};

static PyGetSetDef MenuItem_getset[] = {
    {"checked", MenuItem_get_checked, MenuItem_set_checked,
     "Whether the check item is checked.", NULL},
    {NULL}
};

static PyType_Slot MenuItem_slots[] = {
    {Py_tp_doc,       "A menu item. Created by Menu methods, not directly instantiated."},
    {Py_tp_methods,   MenuItem_methods},
    {Py_tp_getset,    MenuItem_getset},
    {Py_tp_dealloc,   MenuItem_dealloc},
    {Py_tp_traverse,  MenuItem_traverse},
    {Py_tp_clear,     MenuItem_clear},
    {0, NULL}
};

PyType_Spec MenuItem_spec = {
    .name      = "libui.core.MenuItem",
    .basicsize = sizeof(UiMenuItemObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = MenuItem_slots,
};

/* -- Menu ---------------------------------------------------------- */

typedef struct {
    PyObject_HEAD
    uiMenu *menu;
    PyObject *items;  /* list of MenuItem objects — prevent GC */
} UiMenuObject;

/* Helper to wrap a raw uiMenuItem* into a Python MenuItem object */
static PyObject *
wrap_menu_item(uiMenuItem *raw)
{
    UiMenuItemObject *mi = PyObject_GC_New(UiMenuItemObject, MenuItemType);
    if (mi == NULL) return NULL;
    mi->item = raw;
    mi->callback = NULL;
    PyObject_GC_Track((PyObject *)mi);
    return (PyObject *)mi;
}

static int
Menu_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"name", NULL};
    const char *name;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &name))
        return -1;

    UiMenuObject *m = (UiMenuObject *)self;
    m->menu = uiNewMenu(name);
    if (m->menu == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewMenu failed");
        return -1;
    }
    m->items = PyList_New(0);
    if (m->items == NULL) return -1;
    return 0;
}

static PyObject *
Menu_append_item(PyObject *self, PyObject *args)
{
    const char *name;
    if (!PyArg_ParseTuple(args, "s", &name))
        return NULL;
    UiMenuObject *m = (UiMenuObject *)self;
    uiMenuItem *raw = uiMenuAppendItem(m->menu, name);
    PyObject *item = wrap_menu_item(raw);
    if (item == NULL) return NULL;
    PyList_Append(m->items, item);
    return item;
}

static PyObject *
Menu_append_check_item(PyObject *self, PyObject *args)
{
    const char *name;
    if (!PyArg_ParseTuple(args, "s", &name))
        return NULL;
    UiMenuObject *m = (UiMenuObject *)self;
    uiMenuItem *raw = uiMenuAppendCheckItem(m->menu, name);
    PyObject *item = wrap_menu_item(raw);
    if (item == NULL) return NULL;
    PyList_Append(m->items, item);
    return item;
}

static PyObject *
Menu_append_quit_item(PyObject *self, PyObject *Py_UNUSED(args))
{
    UiMenuObject *m = (UiMenuObject *)self;
    uiMenuItem *raw = uiMenuAppendQuitItem(m->menu);
    PyObject *item = wrap_menu_item(raw);
    if (item == NULL) return NULL;
    PyList_Append(m->items, item);
    return item;
}

static PyObject *
Menu_append_preferences_item(PyObject *self, PyObject *Py_UNUSED(args))
{
    UiMenuObject *m = (UiMenuObject *)self;
    uiMenuItem *raw = uiMenuAppendPreferencesItem(m->menu);
    PyObject *item = wrap_menu_item(raw);
    if (item == NULL) return NULL;
    PyList_Append(m->items, item);
    return item;
}

static PyObject *
Menu_append_about_item(PyObject *self, PyObject *Py_UNUSED(args))
{
    UiMenuObject *m = (UiMenuObject *)self;
    uiMenuItem *raw = uiMenuAppendAboutItem(m->menu);
    PyObject *item = wrap_menu_item(raw);
    if (item == NULL) return NULL;
    PyList_Append(m->items, item);
    return item;
}

static PyObject *
Menu_append_separator(PyObject *self, PyObject *Py_UNUSED(args))
{
    UiMenuObject *m = (UiMenuObject *)self;
    uiMenuAppendSeparator(m->menu);
    Py_RETURN_NONE;
}

static int
Menu_traverse(PyObject *self, visitproc visit, void *arg)
{
    UiMenuObject *m = (UiMenuObject *)self;
    Py_VISIT(m->items);
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static int
Menu_clear(PyObject *self)
{
    UiMenuObject *m = (UiMenuObject *)self;
    Py_CLEAR(m->items);
    return 0;
}

static void
Menu_dealloc(PyObject *self)
{
    PyObject_GC_UnTrack(self);
    Menu_clear(self);
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyMethodDef Menu_methods[] = {
    {"append_item",             Menu_append_item,             METH_VARARGS,
     "append_item(name)\n--\n\nAdd a menu item. Returns the MenuItem."},
    {"append_check_item",       Menu_append_check_item,       METH_VARARGS,
     "append_check_item(name)\n--\n\nAdd a checkable menu item. Returns the MenuItem."},
    {"append_quit_item",        Menu_append_quit_item,        METH_NOARGS,
     "Add a platform Quit menu item."},
    {"append_preferences_item", Menu_append_preferences_item, METH_NOARGS,
     "Add a platform Preferences menu item."},
    {"append_about_item",       Menu_append_about_item,       METH_NOARGS,
     "Add a platform About menu item."},
    {"append_separator",        Menu_append_separator,        METH_NOARGS,
     "Add a separator line."},
    {NULL}
};

static PyType_Slot Menu_slots[] = {
    {Py_tp_doc,       "Menu(name)\n--\n\n"
                      "An application menu. Must be created before any Window."},
    {Py_tp_init,      Menu_init},
    {Py_tp_methods,   Menu_methods},
    {Py_tp_dealloc,   Menu_dealloc},
    {Py_tp_traverse,  Menu_traverse},
    {Py_tp_clear,     Menu_clear},
    {0, NULL}
};

PyType_Spec Menu_spec = {
    .name      = "libui.core.Menu",
    .basicsize = sizeof(UiMenuObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = Menu_slots,
};
