/*
 * module.c — Module definition, module-level functions, PyInit.
 */
#include "module.h"

/* -- Global asyncio loop ------------------------------------------- */

PyObject *g_asyncio_loop = NULL;

/* -- Global type pointers ------------------------------------------ */

PyTypeObject *ControlType          = NULL;
PyTypeObject *WindowType           = NULL;
PyTypeObject *ButtonType           = NULL;
PyTypeObject *LabelType            = NULL;
PyTypeObject *BoxType              = NULL;
PyTypeObject *VerticalBoxType      = NULL;
PyTypeObject *HorizontalBoxType    = NULL;
PyTypeObject *EntryType            = NULL;
PyTypeObject *CheckboxType         = NULL;
PyTypeObject *ComboboxType         = NULL;
PyTypeObject *TabType              = NULL;
PyTypeObject *GroupType            = NULL;
PyTypeObject *SpinboxType          = NULL;
PyTypeObject *SliderType           = NULL;
PyTypeObject *ProgressBarType      = NULL;
PyTypeObject *SeparatorType        = NULL;
PyTypeObject *EditableComboboxType = NULL;
PyTypeObject *RadioButtonsType     = NULL;
PyTypeObject *DateTimePickerType   = NULL;
PyTypeObject *MultilineEntryType   = NULL;
PyTypeObject *ColorButtonType      = NULL;
PyTypeObject *FontButtonType       = NULL;
PyTypeObject *FormType             = NULL;
PyTypeObject *GridType             = NULL;
PyTypeObject *MenuType             = NULL;
PyTypeObject *MenuItemType         = NULL;

/* Complex widget type pointers */
PyTypeObject *ImageType              = NULL;
PyTypeObject *OpenTypeFeaturesType   = NULL;
PyTypeObject *AttributeType          = NULL;
PyTypeObject *AttributedStringType   = NULL;
PyTypeObject *DrawPathType           = NULL;
PyTypeObject *DrawBrushType          = NULL;
PyTypeObject *DrawStrokeParamsType   = NULL;
PyTypeObject *DrawMatrixType         = NULL;
PyTypeObject *DrawContextType        = NULL;
PyTypeObject *DrawTextLayoutType     = NULL;
PyTypeObject *AreaType               = NULL;
PyTypeObject *ScrollingAreaType      = NULL;
PyTypeObject *TableModelType         = NULL;
PyTypeObject *TableType              = NULL;

/* -- Module-level functions ---------------------------------------- */

static PyObject *
mod_init(PyObject *Py_UNUSED(self), PyObject *Py_UNUSED(args))
{
    uiInitOptions opts = {.Size = sizeof(uiInitOptions)};
    const char *err = uiInit(&opts);
    if (err != NULL) {
        PyErr_Format(PyExc_RuntimeError, "uiInit failed: %s", err);
        uiFreeInitError(err);
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyObject *
mod_uninit(PyObject *Py_UNUSED(self), PyObject *Py_UNUSED(args))
{
    uninit_all_controls();
    uiUninit();
    Py_RETURN_NONE;
}

static PyObject *
mod_main(PyObject *Py_UNUSED(self), PyObject *Py_UNUSED(args))
{
    Py_BEGIN_ALLOW_THREADS
    uiMain();
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
}

static PyObject *
mod_main_steps(PyObject *Py_UNUSED(self), PyObject *Py_UNUSED(args))
{
    uiMainSteps();
    Py_RETURN_NONE;
}

static PyObject *
mod_main_step(PyObject *Py_UNUSED(self), PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"wait", NULL};
    int wait = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|p", kwlist, &wait))
        return NULL;
    int result;
    Py_BEGIN_ALLOW_THREADS
    result = uiMainStep(wait);
    Py_END_ALLOW_THREADS
    return PyBool_FromLong(result);
}

static PyObject *
mod_quit(PyObject *Py_UNUSED(self), PyObject *Py_UNUSED(args))
{
    uiQuit();
    Py_RETURN_NONE;
}

static PyObject *should_quit_callback = NULL;

static PyObject *
mod_on_should_quit(PyObject *Py_UNUSED(self), PyObject *args)
{
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    if (!PyCallable_Check(callable)) {
        PyErr_SetString(PyExc_TypeError, "callback must be callable");
        return NULL;
    }
    Py_XDECREF(should_quit_callback);
    Py_INCREF(callable);
    should_quit_callback = callable;
    uiOnShouldQuit(trampoline_should_quit, callable);
    Py_RETURN_NONE;
}

/* -- queue_main ---------------------------------------------------- */

static void
queue_main_trampoline(void *data)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *callable = (PyObject *)data;
    PyObject *result = PyObject_CallNoArgs(callable);
    if (result == NULL)
        PyErr_WriteUnraisable(callable);
    else
        Py_DECREF(result);
    Py_DECREF(callable);   /* one-shot: release ref taken at queue time */
    PyGILState_Release(gstate);
}

static PyObject *
mod_queue_main(PyObject *Py_UNUSED(self), PyObject *args)
{
    PyObject *callable;
    if (!PyArg_ParseTuple(args, "O", &callable))
        return NULL;
    if (!PyCallable_Check(callable)) {
        PyErr_SetString(PyExc_TypeError, "argument must be callable");
        return NULL;
    }
    Py_INCREF(callable);
    uiQueueMain(queue_main_trampoline, callable);
    Py_RETURN_NONE;
}

/* -- _set_asyncio_loop --------------------------------------------- */

static PyObject *
mod_set_asyncio_loop(PyObject *Py_UNUSED(self), PyObject *args)
{
    PyObject *loop;
    if (!PyArg_ParseTuple(args, "O", &loop))
        return NULL;
    Py_XDECREF(g_asyncio_loop);
    if (loop == Py_None) {
        g_asyncio_loop = NULL;
    } else {
        Py_INCREF(loop);
        g_asyncio_loop = loop;
    }
    Py_RETURN_NONE;
}

/* -- Dialog functions ---------------------------------------------- */

static PyObject *
mod_open_file(PyObject *Py_UNUSED(self), PyObject *args)
{
    PyObject *win_obj;
    if (!PyArg_ParseTuple(args, "O!", WindowType, &win_obj))
        return NULL;
    if (check_control(as_ctrl(win_obj)) < 0) return NULL;
    char *path = uiOpenFile(uiWindow(as_ctrl(win_obj)->control));
    if (path == NULL)
        Py_RETURN_NONE;
    PyObject *s = PyUnicode_FromString(path);
    uiFreeText(path);
    return s;
}

static PyObject *
mod_open_folder(PyObject *Py_UNUSED(self), PyObject *args)
{
    PyObject *win_obj;
    if (!PyArg_ParseTuple(args, "O!", WindowType, &win_obj))
        return NULL;
    if (check_control(as_ctrl(win_obj)) < 0) return NULL;
    char *path = uiOpenFolder(uiWindow(as_ctrl(win_obj)->control));
    if (path == NULL)
        Py_RETURN_NONE;
    PyObject *s = PyUnicode_FromString(path);
    uiFreeText(path);
    return s;
}

static PyObject *
mod_save_file(PyObject *Py_UNUSED(self), PyObject *args)
{
    PyObject *win_obj;
    if (!PyArg_ParseTuple(args, "O!", WindowType, &win_obj))
        return NULL;
    if (check_control(as_ctrl(win_obj)) < 0) return NULL;
    char *path = uiSaveFile(uiWindow(as_ctrl(win_obj)->control));
    if (path == NULL)
        Py_RETURN_NONE;
    PyObject *s = PyUnicode_FromString(path);
    uiFreeText(path);
    return s;
}

static PyObject *
mod_msg_box(PyObject *Py_UNUSED(self), PyObject *args)
{
    PyObject *win_obj;
    const char *title, *desc;
    if (!PyArg_ParseTuple(args, "O!ss", WindowType, &win_obj, &title, &desc))
        return NULL;
    if (check_control(as_ctrl(win_obj)) < 0) return NULL;
    uiMsgBox(uiWindow(as_ctrl(win_obj)->control), title, desc);
    Py_RETURN_NONE;
}

static PyObject *
mod_msg_box_error(PyObject *Py_UNUSED(self), PyObject *args)
{
    PyObject *win_obj;
    const char *title, *desc;
    if (!PyArg_ParseTuple(args, "O!ss", WindowType, &win_obj, &title, &desc))
        return NULL;
    if (check_control(as_ctrl(win_obj)) < 0) return NULL;
    uiMsgBoxError(uiWindow(as_ctrl(win_obj)->control), title, desc);
    Py_RETURN_NONE;
}

static PyMethodDef module_methods[] = {
    {"init",                    mod_init,                                        METH_NOARGS,                  "Initialize the UI library. Must be called before creating any controls."},
    {"uninit",                  mod_uninit,                                      METH_NOARGS,                  "Shut down the UI library."},
    {"main",                    mod_main,                                        METH_NOARGS,                  "Run the UI main event loop (blocking)."},
    {"main_steps",              mod_main_steps,                                  METH_NOARGS,                  "Enable non-blocking stepping mode."},
    {"main_step",               (PyCFunction)mod_main_step,                      METH_VARARGS | METH_KEYWORDS, "main_step(wait=False)\n--\n\nProcess one event iteration. Returns True if an event was processed."},
    {"quit",                    mod_quit,                                        METH_NOARGS,                  "Signal the UI event loop to stop."},
    {"on_should_quit",          mod_on_should_quit,                              METH_VARARGS,                 "on_should_quit(callback)\n--\n\nRegister a callback for quit requests. Return True to allow."},
    {"open_file",               mod_open_file,                                   METH_VARARGS,                 "open_file(window)\n--\n\nShow a file open dialog. Returns path or None."},
    {"open_folder",             mod_open_folder,                                 METH_VARARGS,                 "open_folder(window)\n--\n\nShow a folder open dialog. Returns path or None."},
    {"save_file",               mod_save_file,                                   METH_VARARGS,                 "save_file(window)\n--\n\nShow a file save dialog. Returns path or None."},
    {"msg_box",                 mod_msg_box,                                     METH_VARARGS,                 "msg_box(window, title, description)\n--\n\nShow a message box."},
    {"msg_box_error",           mod_msg_box_error,                               METH_VARARGS,                 "msg_box_error(window, title, description)\n--\n\nShow an error message box."},
    {"queue_main",              mod_queue_main,                                  METH_VARARGS,                 "queue_main(callable)\n--\n\nSchedule a callable to run on the main UI thread."},
    {"_set_asyncio_loop",       mod_set_asyncio_loop,                            METH_VARARGS,                 "_set_asyncio_loop(loop)\n--\n\nSet the asyncio event loop for coroutine scheduling. Pass None to clear."},
    /* Attribute factory functions */
    {"family_attribute",        mod_family_attribute,                             METH_VARARGS,                 "family_attribute(family)\n--\n\nCreate a font family attribute."},
    {"size_attribute",          mod_size_attribute,                               METH_VARARGS,                 "size_attribute(size)\n--\n\nCreate a font size attribute."},
    {"weight_attribute",        mod_weight_attribute,                             METH_VARARGS,                 "weight_attribute(weight)\n--\n\nCreate a font weight attribute."},
    {"italic_attribute",        mod_italic_attribute,                             METH_VARARGS,                 "italic_attribute(italic)\n--\n\nCreate a font italic attribute."},
    {"stretch_attribute",       mod_stretch_attribute,                            METH_VARARGS,                 "stretch_attribute(stretch)\n--\n\nCreate a font stretch attribute."},
    {"color_attribute",         mod_color_attribute,                              METH_VARARGS,                 "color_attribute(r, g, b, a)\n--\n\nCreate a text color attribute."},
    {"background_attribute",    mod_background_attribute,                         METH_VARARGS,                 "background_attribute(r, g, b, a)\n--\n\nCreate a background color attribute."},
    {"underline_attribute",     mod_underline_attribute,                          METH_VARARGS,                 "underline_attribute(style)\n--\n\nCreate an underline attribute."},
    {"underline_color_attribute", mod_underline_color_attribute,                  METH_VARARGS,                 "underline_color_attribute(kind, r, g, b, a)\n--\n\nCreate an underline color attribute."},
    {"features_attribute",      mod_features_attribute,                           METH_VARARGS,                 "features_attribute(features)\n--\n\nCreate an OpenType features attribute."},
    {NULL}
};

/* -- Module definition --------------------------------------------- */

static struct PyModuleDef core_module = {
    PyModuleDef_HEAD_INIT,
    .m_name    = "libui.core",
    .m_size    = -1,
    .m_methods = module_methods,
};

/* Helper: create a heap type from spec with a given base */
static PyTypeObject *
make_type(PyObject *module, PyType_Spec *spec, PyTypeObject *base)
{
    PyObject *bases = NULL;
    if (base != NULL) {
        bases = PyTuple_Pack(1, (PyObject *)base);
        if (bases == NULL) return NULL;
    }
    PyObject *type = PyType_FromSpecWithBases(spec, bases);
    Py_XDECREF(bases);
    if (type == NULL) return NULL;

    const char *dot = strrchr(spec->name, '.');
    const char *attr = dot ? dot + 1 : spec->name;
    if (PyModule_AddObject(module, attr, type) < 0) {
        Py_DECREF(type);
        return NULL;
    }
    return (PyTypeObject *)type;
}

/* -- Module init --------------------------------------------------- */

PyMODINIT_FUNC
PyInit_core(void)
{
    PyObject *m = PyModule_Create(&core_module);
    if (m == NULL) return NULL;

    /* -- Base type ------------------------------------------------- */
    ControlType = make_type(m, &Control_spec, NULL);
    if (!ControlType) goto fail;

    /* -- Widget types (inherit from Control) ----------------------- */
    WindowType = make_type(m, &Window_spec, ControlType);
    if (!WindowType) goto fail;

    ButtonType = make_type(m, &Button_spec, ControlType);
    if (!ButtonType) goto fail;

    LabelType = make_type(m, &Label_spec, ControlType);
    if (!LabelType) goto fail;

    BoxType = make_type(m, &Box_spec, ControlType);
    if (!BoxType) goto fail;

    VerticalBoxType = make_type(m, &VerticalBox_spec, BoxType);
    if (!VerticalBoxType) goto fail;

    HorizontalBoxType = make_type(m, &HorizontalBox_spec, BoxType);
    if (!HorizontalBoxType) goto fail;

    EntryType = make_type(m, &Entry_spec, ControlType);
    if (!EntryType) goto fail;

    CheckboxType = make_type(m, &Checkbox_spec, ControlType);
    if (!CheckboxType) goto fail;

    ComboboxType = make_type(m, &Combobox_spec, ControlType);
    if (!ComboboxType) goto fail;

    TabType = make_type(m, &Tab_spec, ControlType);
    if (!TabType) goto fail;

    GroupType = make_type(m, &Group_spec, ControlType);
    if (!GroupType) goto fail;

    SpinboxType = make_type(m, &Spinbox_spec, ControlType);
    if (!SpinboxType) goto fail;

    SliderType = make_type(m, &Slider_spec, ControlType);
    if (!SliderType) goto fail;

    ProgressBarType = make_type(m, &ProgressBar_spec, ControlType);
    if (!ProgressBarType) goto fail;

    SeparatorType = make_type(m, &Separator_spec, ControlType);
    if (!SeparatorType) goto fail;

    EditableComboboxType = make_type(m, &EditableCombobox_spec, ControlType);
    if (!EditableComboboxType) goto fail;

    RadioButtonsType = make_type(m, &RadioButtons_spec, ControlType);
    if (!RadioButtonsType) goto fail;

    DateTimePickerType = make_type(m, &DateTimePicker_spec, ControlType);
    if (!DateTimePickerType) goto fail;

    MultilineEntryType = make_type(m, &MultilineEntry_spec, ControlType);
    if (!MultilineEntryType) goto fail;

    ColorButtonType = make_type(m, &ColorButton_spec, ControlType);
    if (!ColorButtonType) goto fail;

    FontButtonType = make_type(m, &FontButton_spec, ControlType);
    if (!FontButtonType) goto fail;

    FormType = make_type(m, &Form_spec, ControlType);
    if (!FormType) goto fail;

    GridType = make_type(m, &Grid_spec, ControlType);
    if (!GridType) goto fail;

    /* -- Menu types (NOT Control subclasses) ----------------------- */
    MenuItemType = make_type(m, &MenuItem_spec, NULL);
    if (!MenuItemType) goto fail;

    MenuType = make_type(m, &Menu_spec, NULL);
    if (!MenuType) goto fail;

    /* -- Complex widget types (NOT Control subclasses) ------------- */
    ImageType = make_type(m, &Image_spec, NULL);
    if (!ImageType) goto fail;

    OpenTypeFeaturesType = make_type(m, &OpenTypeFeatures_spec, NULL);
    if (!OpenTypeFeaturesType) goto fail;

    AttributeType = make_type(m, &Attribute_spec, NULL);
    if (!AttributeType) goto fail;

    AttributedStringType = make_type(m, &AttributedString_spec, NULL);
    if (!AttributedStringType) goto fail;

    DrawPathType = make_type(m, &DrawPath_spec, NULL);
    if (!DrawPathType) goto fail;

    DrawBrushType = make_type(m, &DrawBrush_spec, NULL);
    if (!DrawBrushType) goto fail;

    DrawStrokeParamsType = make_type(m, &DrawStrokeParams_spec, NULL);
    if (!DrawStrokeParamsType) goto fail;

    DrawMatrixType = make_type(m, &DrawMatrix_spec, NULL);
    if (!DrawMatrixType) goto fail;

    DrawContextType = make_type(m, &DrawContext_spec, NULL);
    if (!DrawContextType) goto fail;

    DrawTextLayoutType = make_type(m, &DrawTextLayout_spec, NULL);
    if (!DrawTextLayoutType) goto fail;

    TableModelType = make_type(m, &TableModel_spec, NULL);
    if (!TableModelType) goto fail;

    /* -- Control subclass types for Area and Table ----------------- */
    AreaType = make_type(m, &Area_spec, ControlType);
    if (!AreaType) goto fail;

    ScrollingAreaType = make_type(m, &ScrollingArea_spec, AreaType);
    if (!ScrollingAreaType) goto fail;

    TableType = make_type(m, &Table_spec, ControlType);
    if (!TableType) goto fail;

    /* -- Enum constants -------------------------------------------- */
    PyObject *enum_mod = PyImport_ImportModule("enum");
    if (!enum_mod) goto fail;
    PyObject *IntEnum = PyObject_GetAttrString(enum_mod, "IntEnum");
    PyObject *IntFlag = PyObject_GetAttrString(enum_mod, "IntFlag");
    Py_DECREF(enum_mod);
    if (!IntEnum || !IntFlag) {
        Py_XDECREF(IntEnum); Py_XDECREF(IntFlag); goto fail;
    }

    if (register_grid_enums(m, IntEnum)            < 0) goto enum_fail;
    if (register_draw_enums(m, IntEnum)            < 0) goto enum_fail;
    if (register_area_enums(m, IntEnum, IntFlag)   < 0) goto enum_fail;
    if (register_attribute_enums(m, IntEnum)       < 0) goto enum_fail;
    if (register_table_enums(m, IntEnum)           < 0) goto enum_fail;

    Py_DECREF(IntEnum);
    Py_DECREF(IntFlag);
    return m;

enum_fail:
    Py_DECREF(IntEnum);
    Py_DECREF(IntFlag);
fail:
    Py_DECREF(m);
    return NULL;
}
