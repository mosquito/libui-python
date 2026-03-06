#ifndef UI_CORE_H
#define UI_CORE_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "ui.h"

/* -- Base object struct -------------------------------------------- */

typedef struct UiControlObject UiControlObject;
struct UiControlObject {
    PyObject_HEAD
    uiControl *control;
    int owned;            /* 1 = Python should destroy on dealloc */
    PyObject *children;   /* list — prevent GC of parented children */
    PyObject *callbacks;  /* dict — strong refs to callback callables */
    /* Intrusive doubly-linked list for tracking all live controls */
    UiControlObject *track_prev;
    UiControlObject *track_next;
};

/* -- Inline helpers ------------------------------------------------ */

static inline UiControlObject *
as_ctrl(PyObject *self)
{
    return (UiControlObject *)self;
}

/* -- Extern type pointers (defined in module.c) -------------------- */

extern PyTypeObject *ControlType;
extern PyTypeObject *WindowType;
extern PyTypeObject *ButtonType;
extern PyTypeObject *LabelType;
extern PyTypeObject *BoxType;
extern PyTypeObject *VerticalBoxType;
extern PyTypeObject *HorizontalBoxType;
extern PyTypeObject *EntryType;
extern PyTypeObject *CheckboxType;
extern PyTypeObject *ComboboxType;
extern PyTypeObject *TabType;
extern PyTypeObject *GroupType;
extern PyTypeObject *SpinboxType;
extern PyTypeObject *SliderType;
extern PyTypeObject *ProgressBarType;
extern PyTypeObject *SeparatorType;
extern PyTypeObject *EditableComboboxType;
extern PyTypeObject *RadioButtonsType;
extern PyTypeObject *DateTimePickerType;
extern PyTypeObject *MultilineEntryType;
extern PyTypeObject *ColorButtonType;
extern PyTypeObject *FontButtonType;
extern PyTypeObject *FormType;
extern PyTypeObject *GridType;
extern PyTypeObject *MenuType;
extern PyTypeObject *MenuItemType;

/* Complex widget types */
extern PyTypeObject *ImageType;
extern PyTypeObject *OpenTypeFeaturesType;
extern PyTypeObject *AttributeType;
extern PyTypeObject *AttributedStringType;
extern PyTypeObject *DrawPathType;
extern PyTypeObject *DrawBrushType;
extern PyTypeObject *DrawStrokeParamsType;
extern PyTypeObject *DrawMatrixType;
extern PyTypeObject *DrawContextType;
extern PyTypeObject *DrawTextLayoutType;
extern PyTypeObject *AreaType;
extern PyTypeObject *ScrollingAreaType;
extern PyTypeObject *TableModelType;
extern PyTypeObject *TableType;

/* -- Main-thread guard (defined in module.c) ----------------------- */

extern unsigned long g_main_thread_id;

static inline int
is_main_thread(void)
{
    return PyThread_get_thread_ident() == g_main_thread_id;
}

#define ENSURE_MAIN_THREAD                                                  \
    do {                                                                    \
        if (!is_main_thread()) {                                            \
            PyErr_SetString(PyExc_RuntimeError,                             \
                "this function must be called from the main UI thread");    \
            return NULL;                                                    \
        }                                                                   \
    } while (0)

#define ENSURE_MAIN_THREAD_INT                                              \
    do {                                                                    \
        if (!is_main_thread()) {                                            \
            PyErr_SetString(PyExc_RuntimeError,                             \
                "this function must be called from the main UI thread");    \
            return -1;                                                      \
        }                                                                   \
    } while (0)

/* -- Resource tracking (non-Control libui objects) ------------------ */

typedef void (*resource_free_fn)(void *);

typedef struct UiResourceNode {
    struct UiResourceNode *res_next;
    struct UiResourceNode *res_prev;
    void **handle_ptr;        /* pointer to the field holding the libui handle */
    resource_free_fn free_fn; /* function to free the handle */
} UiResourceNode;

void track_resource(UiResourceNode *node, void **handle_ptr, resource_free_fn free_fn);
void untrack_resource(UiResourceNode *node);
void uninit_all_resources(void);

/* -- Helpers (defined in control.c) -------------------------------- */

/* Returns -1 + sets RuntimeError if the control already has a parent.
 * Returns 0 if it is safe to set a parent. */
static inline int
check_no_parent(UiControlObject *child)
{
    if (child->control && uiControlParent(child->control) != NULL) {
        PyErr_SetString(PyExc_RuntimeError,
            "control already has a parent; remove it first");
        return -1;
    }
    return 0;
}

int check_control(UiControlObject *self);
int init_base(UiControlObject *self, uiControl *ctrl);
int store_callback(UiControlObject *self, const char *key, PyObject *callable);
void track_control(UiControlObject *c);
void untrack_control(UiControlObject *c);
void uninit_all_controls(void);

/* -- Trampolines (defined in control.c) ---------------------------- */

void trampoline_void(void *sender, void *data);
int  trampoline_int_return(void *sender, void *data);
int  trampoline_should_quit(void *data);

/* -- Invalidation helper (defined in control.c) -------------------- */

void invalidate_control_tree(UiControlObject *c);

/* -- GC / lifecycle (defined in control.c) ------------------------- */

void Control_dealloc(PyObject *self);
int  Control_traverse(PyObject *self, visitproc visit, void *arg);
int  Control_clear(PyObject *self);

/* -- Type specs (defined in respective .c files) ------------------- */

extern PyType_Spec Control_spec;
extern PyType_Spec Window_spec;
extern PyType_Spec Button_spec;
extern PyType_Spec Label_spec;
extern PyType_Spec Box_spec;
extern PyType_Spec VerticalBox_spec;
extern PyType_Spec HorizontalBox_spec;
extern PyType_Spec Entry_spec;
extern PyType_Spec Checkbox_spec;
extern PyType_Spec Combobox_spec;
extern PyType_Spec Tab_spec;
extern PyType_Spec Group_spec;
extern PyType_Spec Spinbox_spec;
extern PyType_Spec Slider_spec;
extern PyType_Spec ProgressBar_spec;
extern PyType_Spec Separator_spec;
extern PyType_Spec EditableCombobox_spec;
extern PyType_Spec RadioButtons_spec;
extern PyType_Spec DateTimePicker_spec;
extern PyType_Spec MultilineEntry_spec;
extern PyType_Spec ColorButton_spec;
extern PyType_Spec FontButton_spec;
extern PyType_Spec Form_spec;
extern PyType_Spec Grid_spec;
extern PyType_Spec Menu_spec;
extern PyType_Spec MenuItem_spec;

/* Complex widget type specs */
extern PyType_Spec Image_spec;
extern PyType_Spec OpenTypeFeatures_spec;
extern PyType_Spec Attribute_spec;
extern PyType_Spec AttributedString_spec;
extern PyType_Spec DrawPath_spec;
extern PyType_Spec DrawBrush_spec;
extern PyType_Spec DrawStrokeParams_spec;
extern PyType_Spec DrawMatrix_spec;
extern PyType_Spec DrawContext_spec;
extern PyType_Spec DrawTextLayout_spec;
extern PyType_Spec Area_spec;
extern PyType_Spec ScrollingArea_spec;
extern PyType_Spec TableModel_spec;
extern PyType_Spec Table_spec;

/* -- Enum helper (used by module.c and per-widget enum registration) -- */

typedef struct { const char *name; int value; } EnumMember;

int add_enum(PyObject *module, PyObject *base,
             const char *cls_name,
             const EnumMember *members, int count);

#define N_MEMBERS(arr) ((int)(sizeof(arr)/sizeof(arr[0])))

/* -- Enum registration functions (defined in respective .c files) --- */

int register_grid_enums(PyObject *module, PyObject *IntEnum);
int register_draw_enums(PyObject *module, PyObject *IntEnum);
int register_area_enums(PyObject *module, PyObject *IntEnum, PyObject *IntFlag);
int register_attribute_enums(PyObject *module, PyObject *IntEnum);
int register_table_enums(PyObject *module, PyObject *IntEnum);

/* -- Asyncio loop (set from Python, used by trampolines) ----------- */

extern PyObject *g_asyncio_loop;

void schedule_coroutine_threadsafe(PyObject *coro, PyObject *callable);

/* Call the registered on_should_quit callback directly, bypassing uiQuit().
 * Used by the window close trampoline to signal the Python event loop
 * without going through Cocoa's [NSApp terminate:] which has reentrancy
 * issues when called from within windowShouldClose:. */
void fire_should_quit(void);

/* -- Attribute factory functions (defined in attribute.c) ----------- */

PyObject *mod_family_attribute(PyObject *self, PyObject *args);
PyObject *mod_size_attribute(PyObject *self, PyObject *args);
PyObject *mod_weight_attribute(PyObject *self, PyObject *args);
PyObject *mod_italic_attribute(PyObject *self, PyObject *args);
PyObject *mod_stretch_attribute(PyObject *self, PyObject *args);
PyObject *mod_color_attribute(PyObject *self, PyObject *args);
PyObject *mod_background_attribute(PyObject *self, PyObject *args);
PyObject *mod_underline_attribute(PyObject *self, PyObject *args);
PyObject *mod_underline_color_attribute(PyObject *self, PyObject *args);
PyObject *mod_features_attribute(PyObject *self, PyObject *args);

#endif /* UI_CORE_H */
