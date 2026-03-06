/*
 * draw.c — DrawPath, DrawBrush, DrawStrokeParams, DrawMatrix,
 *           DrawContext, DrawTextLayout types.
 */
#include "module.h"
#include <string.h>

/* Forward declaration of UiAttributedStringObject from attributed_string.c */
typedef struct {
    PyObject_HEAD
    uiAttributedString *str;
    PyObject *attributes;
} UiAttributedStringObject;

/* Forward declaration — full definition after DrawMatrix */
typedef struct UiDrawTextLayoutObject UiDrawTextLayoutObject;

/* ══════════════════════════════════════════════════════════════════
 *  DrawPath
 * ══════════════════════════════════════════════════════════════════ */

typedef struct {
    PyObject_HEAD
    uiDrawPath *path;
    int ended;
    UiResourceNode res_node;
} UiDrawPathObject;

static int
DrawPath_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"fill_mode", NULL};
    int fill_mode = uiDrawFillModeWinding;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", kwlist, &fill_mode))
        return -1;
    UiDrawPathObject *p = (UiDrawPathObject *)self;
    p->path = uiDrawNewPath((uiDrawFillMode)fill_mode);
    p->ended = 0;
    track_resource(&p->res_node, (void **)&p->path,
                   (resource_free_fn)uiDrawFreePath);
    return 0;
}

static PyObject *
DrawPath_new_figure(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double x, y;
    if (!PyArg_ParseTuple(args, "dd", &x, &y)) return NULL;
    uiDrawPathNewFigure(((UiDrawPathObject *)self)->path, x, y);
    Py_RETURN_NONE;
}

static PyObject *
DrawPath_line_to(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double x, y;
    if (!PyArg_ParseTuple(args, "dd", &x, &y)) return NULL;
    uiDrawPathLineTo(((UiDrawPathObject *)self)->path, x, y);
    Py_RETURN_NONE;
}

static PyObject *
DrawPath_arc_to(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double xc, yc, r, start, sweep;
    int neg = 0;
    if (!PyArg_ParseTuple(args, "ddddd|p", &xc, &yc, &r, &start, &sweep, &neg))
        return NULL;
    uiDrawPathArcTo(((UiDrawPathObject *)self)->path, xc, yc, r, start, sweep, neg);
    Py_RETURN_NONE;
}

static PyObject *
DrawPath_bezier_to(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double c1x, c1y, c2x, c2y, ex, ey;
    if (!PyArg_ParseTuple(args, "dddddd", &c1x, &c1y, &c2x, &c2y, &ex, &ey))
        return NULL;
    uiDrawPathBezierTo(((UiDrawPathObject *)self)->path, c1x, c1y, c2x, c2y, ex, ey);
    Py_RETURN_NONE;
}

static PyObject *
DrawPath_close_figure(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    uiDrawPathCloseFigure(((UiDrawPathObject *)self)->path);
    Py_RETURN_NONE;
}

static PyObject *
DrawPath_add_rectangle(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double x, y, w, h;
    if (!PyArg_ParseTuple(args, "dddd", &x, &y, &w, &h)) return NULL;
    uiDrawPathAddRectangle(((UiDrawPathObject *)self)->path, x, y, w, h);
    Py_RETURN_NONE;
}

static PyObject *
DrawPath_end(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    UiDrawPathObject *p = (UiDrawPathObject *)self;
    uiDrawPathEnd(p->path);
    p->ended = 1;
    Py_RETURN_NONE;
}

static PyObject *
DrawPath_new_figure_with_arc(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double xc, yc, r, start, sweep;
    int neg = 0;
    if (!PyArg_ParseTuple(args, "ddddd|p", &xc, &yc, &r, &start, &sweep, &neg))
        return NULL;
    uiDrawPathNewFigureWithArc(((UiDrawPathObject *)self)->path,
                               xc, yc, r, start, sweep, neg);
    Py_RETURN_NONE;
}

static PyObject *
DrawPath_get_ended(PyObject *self, void *closure)
{
    return PyBool_FromLong(((UiDrawPathObject *)self)->ended);
}

static int
DrawPath_traverse(PyObject *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static void
DrawPath_dealloc(PyObject *self)
{
    UiDrawPathObject *p = (UiDrawPathObject *)self;
    PyObject_GC_UnTrack(self);
    untrack_resource(&p->res_node);
    if (p->path != NULL) {
        uiDrawFreePath(p->path);
        p->path = NULL;
    }
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyMethodDef DrawPath_methods[] = {
    {"new_figure",          DrawPath_new_figure,          METH_VARARGS,
     "new_figure(x, y)\n--\n\nStart a new figure at (x, y)."},
    {"line_to",             DrawPath_line_to,             METH_VARARGS,
     "line_to(x, y)\n--\n\nDraw a line to (x, y)."},
    {"arc_to",              DrawPath_arc_to,              METH_VARARGS,
     "arc_to(xc, yc, radius, start_angle, sweep, negative=False)\n--\n\nDraw an arc."},
    {"bezier_to",           DrawPath_bezier_to,           METH_VARARGS,
     "bezier_to(c1x, c1y, c2x, c2y, end_x, end_y)\n--\n\nDraw a cubic bezier curve."},
    {"close_figure",        DrawPath_close_figure,        METH_NOARGS,
     "Close the current figure."},
    {"add_rectangle",       DrawPath_add_rectangle,       METH_VARARGS,
     "add_rectangle(x, y, width, height)\n--\n\nAdd a rectangle to the path."},
    {"end",                 DrawPath_end,                 METH_NOARGS,
     "Finalize the path for drawing."},
    {"new_figure_with_arc", DrawPath_new_figure_with_arc, METH_VARARGS,
     "new_figure_with_arc(xc, yc, radius, start, sweep, negative=False)\n--\n\n"
     "Start a new figure with an arc."},
    {NULL}
};

static PyGetSetDef DrawPath_getset[] = {
    {"ended", DrawPath_get_ended, NULL,
     "True if the path has been finalized with end().", NULL},
    {NULL}
};

static PyType_Slot DrawPath_slots[] = {
    {Py_tp_doc,       "DrawPath(fill_mode=FillMode.WINDING)\n--\n\nA 2D drawing path."},
    {Py_tp_init,      DrawPath_init},
    {Py_tp_methods,   DrawPath_methods},
    {Py_tp_getset,    DrawPath_getset},
    {Py_tp_dealloc,   DrawPath_dealloc},
    {Py_tp_traverse,  DrawPath_traverse},
    {0, NULL}
};

PyType_Spec DrawPath_spec = {
    .name      = "libui.core.DrawPath",
    .basicsize = sizeof(UiDrawPathObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = DrawPath_slots,
};

/* ══════════════════════════════════════════════════════════════════
 *  DrawBrush
 * ══════════════════════════════════════════════════════════════════ */

typedef struct {
    PyObject_HEAD
    uiDrawBrush brush;
    uiDrawBrushGradientStop *stops;
    size_t num_stops;
} UiDrawBrushObject;

static int
DrawBrush_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    UiDrawBrushObject *b = (UiDrawBrushObject *)self;
    memset(&b->brush, 0, sizeof(b->brush));
    b->brush.Type = uiDrawBrushTypeSolid;
    b->brush.A = 1.0;  /* default opaque black */
    b->stops = NULL;
    b->num_stops = 0;
    return 0;
}

/* Macro for r/w double properties */
#define BRUSH_PROP_DOUBLE(name, field)                                       \
static PyObject *DrawBrush_get_##name(PyObject *self, void *c) {             \
    return PyFloat_FromDouble(((UiDrawBrushObject *)self)->brush.field);      \
}                                                                            \
static int DrawBrush_set_##name(PyObject *self, PyObject *v, void *c) {      \
    double val = PyFloat_AsDouble(v);                                        \
    if (val == -1.0 && PyErr_Occurred()) return -1;                          \
    ((UiDrawBrushObject *)self)->brush.field = val;                          \
    return 0;                                                                \
}

BRUSH_PROP_DOUBLE(r, R)
BRUSH_PROP_DOUBLE(g, G)
BRUSH_PROP_DOUBLE(b, B)
BRUSH_PROP_DOUBLE(a, A)
BRUSH_PROP_DOUBLE(x0, X0)
BRUSH_PROP_DOUBLE(y0, Y0)
BRUSH_PROP_DOUBLE(x1, X1)
BRUSH_PROP_DOUBLE(y1, Y1)
BRUSH_PROP_DOUBLE(outer_radius, OuterRadius)

static PyObject *
DrawBrush_get_type(PyObject *self, void *closure)
{
    return PyLong_FromLong(((UiDrawBrushObject *)self)->brush.Type);
}

static int
DrawBrush_set_type(PyObject *self, PyObject *value, void *closure)
{
    int t = (int)PyLong_AsLong(value);
    if (t == -1 && PyErr_Occurred()) return -1;
    ((UiDrawBrushObject *)self)->brush.Type = (uiDrawBrushType)t;
    return 0;
}

static PyObject *
DrawBrush_set_stops(PyObject *self, PyObject *args)
{
    PyObject *list;
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &list)) return NULL;

    UiDrawBrushObject *b = (UiDrawBrushObject *)self;
    Py_ssize_t n = PyList_Size(list);

    /* Free old stops */
    if (b->stops != NULL) {
        PyMem_Free(b->stops);
        b->stops = NULL;
    }

    if (n == 0) {
        b->brush.Stops = NULL;
        b->brush.NumStops = 0;
        b->num_stops = 0;
        Py_RETURN_NONE;
    }

    b->stops = PyMem_Malloc(sizeof(uiDrawBrushGradientStop) * n);
    if (b->stops == NULL) return PyErr_NoMemory();
    b->num_stops = (size_t)n;

    for (Py_ssize_t i = 0; i < n; i++) {
        PyObject *item = PyList_GetItem(list, i);
        double pos, r, g, b_val, a;
        if (!PyArg_ParseTuple(item, "ddddd", &pos, &r, &g, &b_val, &a)) {
            PyMem_Free(b->stops);
            b->stops = NULL;
            b->num_stops = 0;
            return NULL;
        }
        b->stops[i].Pos = pos;
        b->stops[i].R = r;
        b->stops[i].G = g;
        b->stops[i].B = b_val;
        b->stops[i].A = a;
    }

    b->brush.Stops = b->stops;
    b->brush.NumStops = b->num_stops;
    Py_RETURN_NONE;
}

static int
DrawBrush_traverse(PyObject *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static void
DrawBrush_dealloc(PyObject *self)
{
    UiDrawBrushObject *b = (UiDrawBrushObject *)self;
    PyObject_GC_UnTrack(self);
    if (b->stops != NULL) {
        PyMem_Free(b->stops);
        b->stops = NULL;
    }
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyMethodDef DrawBrush_methods[] = {
    {"set_stops", DrawBrush_set_stops, METH_VARARGS,
     "set_stops(stops)\n--\n\nSet gradient stops. Each stop is (pos, r, g, b, a)."},
    {NULL}
};

static PyGetSetDef DrawBrush_getset[] = {
    {"type",         DrawBrush_get_type, DrawBrush_set_type,
     "Brush type (BrushType enum).", NULL},
    {"r",            DrawBrush_get_r,    DrawBrush_set_r,
     "Red component (0.0-1.0).", NULL},
    {"g",            DrawBrush_get_g,    DrawBrush_set_g,
     "Green component (0.0-1.0).", NULL},
    {"b",            DrawBrush_get_b,    DrawBrush_set_b,
     "Blue component (0.0-1.0).", NULL},
    {"a",            DrawBrush_get_a,    DrawBrush_set_a,
     "Alpha component (0.0-1.0).", NULL},
    {"x0",           DrawBrush_get_x0,   DrawBrush_set_x0,
     "Gradient start X.", NULL},
    {"y0",           DrawBrush_get_y0,   DrawBrush_set_y0,
     "Gradient start Y.", NULL},
    {"x1",           DrawBrush_get_x1,   DrawBrush_set_x1,
     "Gradient end X.", NULL},
    {"y1",           DrawBrush_get_y1,   DrawBrush_set_y1,
     "Gradient end Y.", NULL},
    {"outer_radius", DrawBrush_get_outer_radius, DrawBrush_set_outer_radius,
     "Radial gradient outer radius.", NULL},
    {NULL}
};

static PyType_Slot DrawBrush_slots[] = {
    {Py_tp_doc,       "DrawBrush()\n--\n\nA brush for filling or stroking paths."},
    {Py_tp_init,      DrawBrush_init},
    {Py_tp_methods,   DrawBrush_methods},
    {Py_tp_getset,    DrawBrush_getset},
    {Py_tp_dealloc,   DrawBrush_dealloc},
    {Py_tp_traverse,  DrawBrush_traverse},
    {0, NULL}
};

PyType_Spec DrawBrush_spec = {
    .name      = "libui.core.DrawBrush",
    .basicsize = sizeof(UiDrawBrushObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = DrawBrush_slots,
};

/* ══════════════════════════════════════════════════════════════════
 *  DrawStrokeParams
 * ══════════════════════════════════════════════════════════════════ */

typedef struct {
    PyObject_HEAD
    uiDrawStrokeParams params;
    double *dashes;
    size_t num_dashes;
} UiDrawStrokeParamsObject;

static int
DrawStrokeParams_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    UiDrawStrokeParamsObject *p = (UiDrawStrokeParamsObject *)self;
    memset(&p->params, 0, sizeof(p->params));
    p->params.Cap = uiDrawLineCapFlat;
    p->params.Join = uiDrawLineJoinMiter;
    p->params.Thickness = 1.0;
    p->params.MiterLimit = uiDrawDefaultMiterLimit;
    p->dashes = NULL;
    p->num_dashes = 0;
    return 0;
}

#define SP_PROP_INT(name, field, type)                                        \
static PyObject *DrawSP_get_##name(PyObject *self, void *c) {                \
    return PyLong_FromLong(((UiDrawStrokeParamsObject *)self)->params.field); \
}                                                                            \
static int DrawSP_set_##name(PyObject *self, PyObject *v, void *c) {         \
    int val = (int)PyLong_AsLong(v);                                         \
    if (val == -1 && PyErr_Occurred()) return -1;                            \
    ((UiDrawStrokeParamsObject *)self)->params.field = (type)val;            \
    return 0;                                                                \
}

#define SP_PROP_DOUBLE(name, field)                                           \
static PyObject *DrawSP_get_##name(PyObject *self, void *c) {                \
    return PyFloat_FromDouble(((UiDrawStrokeParamsObject *)self)->params.field); \
}                                                                            \
static int DrawSP_set_##name(PyObject *self, PyObject *v, void *c) {         \
    double val = PyFloat_AsDouble(v);                                        \
    if (val == -1.0 && PyErr_Occurred()) return -1;                          \
    ((UiDrawStrokeParamsObject *)self)->params.field = val;                  \
    return 0;                                                                \
}

SP_PROP_INT(cap, Cap, uiDrawLineCap)
SP_PROP_INT(join, Join, uiDrawLineJoin)
SP_PROP_DOUBLE(thickness, Thickness)
SP_PROP_DOUBLE(miter_limit, MiterLimit)
SP_PROP_DOUBLE(dash_phase, DashPhase)

static PyObject *
DrawStrokeParams_set_dashes(PyObject *self, PyObject *args)
{
    PyObject *list;
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &list)) return NULL;

    UiDrawStrokeParamsObject *p = (UiDrawStrokeParamsObject *)self;
    Py_ssize_t n = PyList_Size(list);

    if (p->dashes != NULL) {
        PyMem_Free(p->dashes);
        p->dashes = NULL;
    }

    if (n == 0) {
        p->params.Dashes = NULL;
        p->params.NumDashes = 0;
        p->num_dashes = 0;
        Py_RETURN_NONE;
    }

    p->dashes = PyMem_Malloc(sizeof(double) * n);
    if (p->dashes == NULL) return PyErr_NoMemory();
    p->num_dashes = (size_t)n;

    for (Py_ssize_t i = 0; i < n; i++) {
        PyObject *item = PyList_GetItem(list, i);
        double val = PyFloat_AsDouble(item);
        if (val == -1.0 && PyErr_Occurred()) {
            PyMem_Free(p->dashes);
            p->dashes = NULL;
            p->num_dashes = 0;
            return NULL;
        }
        p->dashes[i] = val;
    }

    p->params.Dashes = p->dashes;
    p->params.NumDashes = p->num_dashes;
    Py_RETURN_NONE;
}

static int
DrawStrokeParams_traverse(PyObject *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static void
DrawStrokeParams_dealloc(PyObject *self)
{
    UiDrawStrokeParamsObject *p = (UiDrawStrokeParamsObject *)self;
    PyObject_GC_UnTrack(self);
    if (p->dashes != NULL) {
        PyMem_Free(p->dashes);
        p->dashes = NULL;
    }
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyMethodDef DrawStrokeParams_methods[] = {
    {"set_dashes", DrawStrokeParams_set_dashes, METH_VARARGS,
     "set_dashes(dashes)\n--\n\nSet the dash pattern as a list of floats."},
    {NULL}
};

static PyGetSetDef DrawStrokeParams_getset[] = {
    {"cap",         DrawSP_get_cap,         DrawSP_set_cap,
     "Line cap style (LineCap enum).", NULL},
    {"join",        DrawSP_get_join,        DrawSP_set_join,
     "Line join style (LineJoin enum).", NULL},
    {"thickness",   DrawSP_get_thickness,   DrawSP_set_thickness,
     "Line thickness.", NULL},
    {"miter_limit", DrawSP_get_miter_limit, DrawSP_set_miter_limit,
     "Miter limit for miter joins.", NULL},
    {"dash_phase",  DrawSP_get_dash_phase,  DrawSP_set_dash_phase,
     "Dash pattern phase offset.", NULL},
    {NULL}
};

static PyType_Slot DrawStrokeParams_slots[] = {
    {Py_tp_doc,       "DrawStrokeParams()\n--\n\nParameters for stroking a path."},
    {Py_tp_init,      DrawStrokeParams_init},
    {Py_tp_methods,   DrawStrokeParams_methods},
    {Py_tp_getset,    DrawStrokeParams_getset},
    {Py_tp_dealloc,   DrawStrokeParams_dealloc},
    {Py_tp_traverse,  DrawStrokeParams_traverse},
    {0, NULL}
};

PyType_Spec DrawStrokeParams_spec = {
    .name      = "libui.core.DrawStrokeParams",
    .basicsize = sizeof(UiDrawStrokeParamsObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = DrawStrokeParams_slots,
};

/* ══════════════════════════════════════════════════════════════════
 *  DrawMatrix
 * ══════════════════════════════════════════════════════════════════ */

typedef struct {
    PyObject_HEAD
    uiDrawMatrix matrix;
} UiDrawMatrixObject;

static int
DrawMatrix_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    UiDrawMatrixObject *m = (UiDrawMatrixObject *)self;
    uiDrawMatrixSetIdentity(&m->matrix);
    return 0;
}

#define MATRIX_PROP(name, field)                                              \
static PyObject *DrawMatrix_get_##name(PyObject *self, void *c) {            \
    return PyFloat_FromDouble(((UiDrawMatrixObject *)self)->matrix.field);    \
}                                                                            \
static int DrawMatrix_set_##name(PyObject *self, PyObject *v, void *c) {     \
    double val = PyFloat_AsDouble(v);                                        \
    if (val == -1.0 && PyErr_Occurred()) return -1;                          \
    ((UiDrawMatrixObject *)self)->matrix.field = val;                        \
    return 0;                                                                \
}

MATRIX_PROP(m11, M11)
MATRIX_PROP(m12, M12)
MATRIX_PROP(m21, M21)
MATRIX_PROP(m22, M22)
MATRIX_PROP(m31, M31)
MATRIX_PROP(m32, M32)

static PyObject *
DrawMatrix_set_identity(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    uiDrawMatrixSetIdentity(&((UiDrawMatrixObject *)self)->matrix);
    Py_RETURN_NONE;
}

static PyObject *
DrawMatrix_translate(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double x, y;
    if (!PyArg_ParseTuple(args, "dd", &x, &y)) return NULL;
    uiDrawMatrixTranslate(&((UiDrawMatrixObject *)self)->matrix, x, y);
    Py_RETURN_NONE;
}

static PyObject *
DrawMatrix_scale(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double xc, yc, x, y;
    if (!PyArg_ParseTuple(args, "dddd", &xc, &yc, &x, &y)) return NULL;
    uiDrawMatrixScale(&((UiDrawMatrixObject *)self)->matrix, xc, yc, x, y);
    Py_RETURN_NONE;
}

static PyObject *
DrawMatrix_rotate(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double x, y, amount;
    if (!PyArg_ParseTuple(args, "ddd", &x, &y, &amount)) return NULL;
    uiDrawMatrixRotate(&((UiDrawMatrixObject *)self)->matrix, x, y, amount);
    Py_RETURN_NONE;
}

static PyObject *
DrawMatrix_skew(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double x, y, xa, ya;
    if (!PyArg_ParseTuple(args, "dddd", &x, &y, &xa, &ya)) return NULL;
    uiDrawMatrixSkew(&((UiDrawMatrixObject *)self)->matrix, x, y, xa, ya);
    Py_RETURN_NONE;
}

static PyObject *
DrawMatrix_multiply(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    PyObject *other_obj;
    if (!PyArg_ParseTuple(args, "O!", DrawMatrixType, &other_obj)) return NULL;
    uiDrawMatrixMultiply(&((UiDrawMatrixObject *)self)->matrix,
                         &((UiDrawMatrixObject *)other_obj)->matrix);
    Py_RETURN_NONE;
}

static PyObject *
DrawMatrix_invertible(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    return PyBool_FromLong(
        uiDrawMatrixInvertible(&((UiDrawMatrixObject *)self)->matrix));
}

static PyObject *
DrawMatrix_invert(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    return PyBool_FromLong(
        uiDrawMatrixInvert(&((UiDrawMatrixObject *)self)->matrix));
}

static PyObject *
DrawMatrix_transform_point(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double x, y;
    if (!PyArg_ParseTuple(args, "dd", &x, &y)) return NULL;
    uiDrawMatrixTransformPoint(&((UiDrawMatrixObject *)self)->matrix, &x, &y);
    return Py_BuildValue("(dd)", x, y);
}

static PyObject *
DrawMatrix_transform_size(PyObject *self, PyObject *args)
{
    ENSURE_MAIN_THREAD;
    double x, y;
    if (!PyArg_ParseTuple(args, "dd", &x, &y)) return NULL;
    uiDrawMatrixTransformSize(&((UiDrawMatrixObject *)self)->matrix, &x, &y);
    return Py_BuildValue("(dd)", x, y);
}

static int
DrawMatrix_traverse(PyObject *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static void
DrawMatrix_dealloc(PyObject *self)
{
    PyObject_GC_UnTrack(self);
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyMethodDef DrawMatrix_methods[] = {
    {"set_identity",    DrawMatrix_set_identity,    METH_NOARGS,
     "Reset to the identity matrix."},
    {"translate",       DrawMatrix_translate,       METH_VARARGS,
     "translate(x, y)\n--\n\nApply a translation."},
    {"scale",           DrawMatrix_scale,           METH_VARARGS,
     "scale(xc, yc, x, y)\n--\n\nApply a scale around (xc, yc)."},
    {"rotate",          DrawMatrix_rotate,          METH_VARARGS,
     "rotate(x, y, degrees)\n--\n\nApply a rotation around (x, y)."},
    {"skew",            DrawMatrix_skew,            METH_VARARGS,
     "skew(x, y, x_amount, y_amount)\n--\n\nApply a skew."},
    {"multiply",        DrawMatrix_multiply,        METH_VARARGS,
     "multiply(other)\n--\n\nMultiply with another matrix in place."},
    {"invertible",      DrawMatrix_invertible,      METH_NOARGS,
     "Return True if the matrix is invertible."},
    {"invert",          DrawMatrix_invert,          METH_NOARGS,
     "Invert the matrix in place. Returns True on success."},
    {"transform_point", DrawMatrix_transform_point, METH_VARARGS,
     "transform_point(x, y)\n--\n\nReturn the transformed (x, y) point."},
    {"transform_size",  DrawMatrix_transform_size,  METH_VARARGS,
     "transform_size(x, y)\n--\n\nReturn the transformed (x, y) size."},
    {NULL}
};

static PyGetSetDef DrawMatrix_getset[] = {
    {"m11", DrawMatrix_get_m11, DrawMatrix_set_m11, "Matrix element [1,1].", NULL},
    {"m12", DrawMatrix_get_m12, DrawMatrix_set_m12, "Matrix element [1,2].", NULL},
    {"m21", DrawMatrix_get_m21, DrawMatrix_set_m21, "Matrix element [2,1].", NULL},
    {"m22", DrawMatrix_get_m22, DrawMatrix_set_m22, "Matrix element [2,2].", NULL},
    {"m31", DrawMatrix_get_m31, DrawMatrix_set_m31, "Matrix element [3,1] (X translation).", NULL},
    {"m32", DrawMatrix_get_m32, DrawMatrix_set_m32, "Matrix element [3,2] (Y translation).", NULL},
    {NULL}
};

static PyType_Slot DrawMatrix_slots[] = {
    {Py_tp_doc,       "DrawMatrix()\n--\n\nA 2D transformation matrix, initialized to identity."},
    {Py_tp_init,      DrawMatrix_init},
    {Py_tp_methods,   DrawMatrix_methods},
    {Py_tp_getset,    DrawMatrix_getset},
    {Py_tp_dealloc,   DrawMatrix_dealloc},
    {Py_tp_traverse,  DrawMatrix_traverse},
    {0, NULL}
};

PyType_Spec DrawMatrix_spec = {
    .name      = "libui.core.DrawMatrix",
    .basicsize = sizeof(UiDrawMatrixObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = DrawMatrix_slots,
};

/* UiDrawTextLayoutObject — defined here so DrawCtx_text can access it */
struct UiDrawTextLayoutObject {
    PyObject_HEAD
    uiDrawTextLayout *layout;
    PyObject *string_ref;  /* strong ref to AttributedString */
    UiResourceNode res_node;
};

/* ══════════════════════════════════════════════════════════════════
 *  DrawContext (transient, no public constructor)
 * ══════════════════════════════════════════════════════════════════ */

typedef struct {
    PyObject_HEAD
    uiDrawContext *ctx;
    int valid;
} UiDrawContextObject;

#define CHECK_CTX(c) do {                                                     \
    if (!((UiDrawContextObject *)(c))->valid) {                               \
        PyErr_SetString(PyExc_RuntimeError,                                   \
            "DrawContext is only valid during the draw callback");             \
        return NULL;                                                          \
    }                                                                         \
} while (0)

static PyObject *
DrawCtx_fill(PyObject *self, PyObject *args)
{
    CHECK_CTX(self);
    PyObject *path_obj, *brush_obj;
    if (!PyArg_ParseTuple(args, "O!O!",
                          DrawPathType, &path_obj,
                          DrawBrushType, &brush_obj))
        return NULL;
    UiDrawContextObject *c = (UiDrawContextObject *)self;
    uiDrawFill(c->ctx,
               ((UiDrawPathObject *)path_obj)->path,
               &((UiDrawBrushObject *)brush_obj)->brush);
    Py_RETURN_NONE;
}

static PyObject *
DrawCtx_stroke(PyObject *self, PyObject *args)
{
    CHECK_CTX(self);
    PyObject *path_obj, *brush_obj, *params_obj;
    if (!PyArg_ParseTuple(args, "O!O!O!",
                          DrawPathType, &path_obj,
                          DrawBrushType, &brush_obj,
                          DrawStrokeParamsType, &params_obj))
        return NULL;
    UiDrawContextObject *c = (UiDrawContextObject *)self;
    uiDrawStroke(c->ctx,
                 ((UiDrawPathObject *)path_obj)->path,
                 &((UiDrawBrushObject *)brush_obj)->brush,
                 &((UiDrawStrokeParamsObject *)params_obj)->params);
    Py_RETURN_NONE;
}

static PyObject *
DrawCtx_transform(PyObject *self, PyObject *args)
{
    CHECK_CTX(self);
    PyObject *matrix_obj;
    if (!PyArg_ParseTuple(args, "O!", DrawMatrixType, &matrix_obj))
        return NULL;
    UiDrawContextObject *c = (UiDrawContextObject *)self;
    uiDrawTransform(c->ctx, &((UiDrawMatrixObject *)matrix_obj)->matrix);
    Py_RETURN_NONE;
}

static PyObject *
DrawCtx_clip(PyObject *self, PyObject *args)
{
    CHECK_CTX(self);
    PyObject *path_obj;
    if (!PyArg_ParseTuple(args, "O!", DrawPathType, &path_obj))
        return NULL;
    UiDrawContextObject *c = (UiDrawContextObject *)self;
    uiDrawClip(c->ctx, ((UiDrawPathObject *)path_obj)->path);
    Py_RETURN_NONE;
}

static PyObject *
DrawCtx_save(PyObject *self, PyObject *Py_UNUSED(args))
{
    CHECK_CTX(self);
    uiDrawSave(((UiDrawContextObject *)self)->ctx);
    Py_RETURN_NONE;
}

static PyObject *
DrawCtx_restore(PyObject *self, PyObject *Py_UNUSED(args))
{
    CHECK_CTX(self);
    uiDrawRestore(((UiDrawContextObject *)self)->ctx);
    Py_RETURN_NONE;
}

static PyObject *
DrawCtx_text(PyObject *self, PyObject *args)
{
    CHECK_CTX(self);
    PyObject *layout_obj;
    double x, y;
    if (!PyArg_ParseTuple(args, "O!dd", DrawTextLayoutType, &layout_obj, &x, &y))
        return NULL;
    UiDrawContextObject *c = (UiDrawContextObject *)self;
    /* DrawTextLayout stores its layout pointer; access it */
    UiDrawTextLayoutObject *tl = (UiDrawTextLayoutObject *)layout_obj;
    uiDrawText(c->ctx, tl->layout, x, y);
    Py_RETURN_NONE;
}

static int
DrawCtx_traverse(PyObject *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static void
DrawCtx_dealloc(PyObject *self)
{
    PyObject_GC_UnTrack(self);
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyMethodDef DrawCtx_methods[] = {
    {"fill",      DrawCtx_fill,      METH_VARARGS,
     "fill(path, brush)\n--\n\nFill a path with a brush."},
    {"stroke",    DrawCtx_stroke,    METH_VARARGS,
     "stroke(path, brush, stroke_params)\n--\n\nStroke a path."},
    {"transform", DrawCtx_transform, METH_VARARGS,
     "transform(matrix)\n--\n\nApply a transformation matrix."},
    {"clip",      DrawCtx_clip,      METH_VARARGS,
     "clip(path)\n--\n\nClip to a path."},
    {"save",      DrawCtx_save,      METH_NOARGS,
     "Save the current graphics state."},
    {"restore",   DrawCtx_restore,   METH_NOARGS,
     "Restore the previously saved graphics state."},
    {"text",      DrawCtx_text,      METH_VARARGS,
     "text(layout, x, y)\n--\n\nDraw a text layout at (x, y)."},
    {NULL}
};

static PyType_Slot DrawCtx_slots[] = {
    {Py_tp_doc,       "A drawing context. Only valid during an Area draw callback."},
    {Py_tp_methods,   DrawCtx_methods},
    {Py_tp_dealloc,   DrawCtx_dealloc},
    {Py_tp_traverse,  DrawCtx_traverse},
    {0, NULL}
};

PyType_Spec DrawContext_spec = {
    .name      = "libui.core.DrawContext",
    .basicsize = sizeof(UiDrawContextObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = DrawCtx_slots,
};

/* ══════════════════════════════════════════════════════════════════
 *  DrawTextLayout
 * ══════════════════════════════════════════════════════════════════ */

static int
DrawTextLayout_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ENSURE_MAIN_THREAD_INT;
    static char *kwlist[] = {"string", "default_font", "width", "align", NULL};
    PyObject *str_obj, *font_dict;
    double width;
    int align = uiDrawTextAlignLeft;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!d|i", kwlist,
                                     AttributedStringType, &str_obj,
                                     &PyDict_Type, &font_dict,
                                     &width, &align))
        return -1;

    /* Build uiFontDescriptor from dict */
    uiFontDescriptor desc;
    memset(&desc, 0, sizeof(desc));

    PyObject *family = PyDict_GetItemString(font_dict, "family");
    if (family == NULL || !PyUnicode_Check(family)) {
        PyErr_SetString(PyExc_ValueError, "default_font must have 'family' (str)");
        return -1;
    }
    desc.Family = (char *)PyUnicode_AsUTF8(family);

    PyObject *size = PyDict_GetItemString(font_dict, "size");
    if (size == NULL) {
        PyErr_SetString(PyExc_ValueError, "default_font must have 'size'");
        return -1;
    }
    desc.Size = PyFloat_AsDouble(size);
    if (desc.Size == -1.0 && PyErr_Occurred()) return -1;

    PyObject *weight = PyDict_GetItemString(font_dict, "weight");
    desc.Weight = weight ? (uiTextWeight)PyLong_AsLong(weight) : uiTextWeightNormal;

    PyObject *italic = PyDict_GetItemString(font_dict, "italic");
    desc.Italic = italic ? (uiTextItalic)PyLong_AsLong(italic) : uiTextItalicNormal;

    PyObject *stretch = PyDict_GetItemString(font_dict, "stretch");
    desc.Stretch = stretch ? (uiTextStretch)PyLong_AsLong(stretch) : uiTextStretchNormal;

    UiAttributedStringObject *astr = (UiAttributedStringObject *)str_obj;

    uiDrawTextLayoutParams params;
    params.String = astr->str;
    params.DefaultFont = &desc;
    params.Width = width;
    params.Align = (uiDrawTextAlign)align;

    UiDrawTextLayoutObject *tl = (UiDrawTextLayoutObject *)self;
    tl->layout = uiDrawNewTextLayout(&params);
    if (tl->layout == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiDrawNewTextLayout failed");
        return -1;
    }
    Py_INCREF(str_obj);
    tl->string_ref = str_obj;
    track_resource(&tl->res_node, (void **)&tl->layout,
                   (resource_free_fn)uiDrawFreeTextLayout);
    return 0;
}

static PyObject *
DrawTextLayout_extents(PyObject *self, PyObject *Py_UNUSED(args))
{
    ENSURE_MAIN_THREAD;
    UiDrawTextLayoutObject *tl = (UiDrawTextLayoutObject *)self;
    double w, h;
    uiDrawTextLayoutExtents(tl->layout, &w, &h);
    return Py_BuildValue("(dd)", w, h);
}

static int
DrawTextLayout_traverse(PyObject *self, visitproc visit, void *arg)
{
    UiDrawTextLayoutObject *tl = (UiDrawTextLayoutObject *)self;
    Py_VISIT(tl->string_ref);
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static int
DrawTextLayout_clear(PyObject *self)
{
    UiDrawTextLayoutObject *tl = (UiDrawTextLayoutObject *)self;
    Py_CLEAR(tl->string_ref);
    return 0;
}

static void
DrawTextLayout_dealloc(PyObject *self)
{
    UiDrawTextLayoutObject *tl = (UiDrawTextLayoutObject *)self;
    PyObject_GC_UnTrack(self);
    untrack_resource(&tl->res_node);
    DrawTextLayout_clear(self);
    if (tl->layout != NULL) {
        uiDrawFreeTextLayout(tl->layout);
        tl->layout = NULL;
    }
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyMethodDef DrawTextLayout_methods[] = {
    {"extents", DrawTextLayout_extents, METH_NOARGS,
     "Return the (width, height) of the laid-out text."},
    {NULL}
};

static PyType_Slot DrawTextLayout_slots[] = {
    {Py_tp_doc,       "DrawTextLayout(string, default_font, width, align=TextAlign.LEFT)\n--\n\n"
                      "A laid-out text for drawing."},
    {Py_tp_init,      DrawTextLayout_init},
    {Py_tp_methods,   DrawTextLayout_methods},
    {Py_tp_dealloc,   DrawTextLayout_dealloc},
    {Py_tp_traverse,  DrawTextLayout_traverse},
    {Py_tp_clear,     DrawTextLayout_clear},
    {0, NULL}
};

PyType_Spec DrawTextLayout_spec = {
    .name      = "libui.core.DrawTextLayout",
    .basicsize = sizeof(UiDrawTextLayoutObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = DrawTextLayout_slots,
};

/* -- Drawing enums ------------------------------------------------- */

static const EnumMember brush_type_members[] = {
    {"SOLID",           uiDrawBrushTypeSolid},
    {"LINEAR_GRADIENT", uiDrawBrushTypeLinearGradient},
    {"RADIAL_GRADIENT", uiDrawBrushTypeRadialGradient},
    {"IMAGE",           uiDrawBrushTypeImage},
};

static const EnumMember line_cap_members[] = {
    {"FLAT",   uiDrawLineCapFlat},
    {"ROUND",  uiDrawLineCapRound},
    {"SQUARE", uiDrawLineCapSquare},
};

static const EnumMember line_join_members[] = {
    {"MITER", uiDrawLineJoinMiter},
    {"ROUND", uiDrawLineJoinRound},
    {"BEVEL", uiDrawLineJoinBevel},
};

static const EnumMember fill_mode_members[] = {
    {"WINDING",   uiDrawFillModeWinding},
    {"ALTERNATE", uiDrawFillModeAlternate},
};

static const EnumMember text_align_members[] = {
    {"LEFT",   uiDrawTextAlignLeft},
    {"CENTER", uiDrawTextAlignCenter},
    {"RIGHT",  uiDrawTextAlignRight},
};

int
register_draw_enums(PyObject *module, PyObject *IntEnum)
{
    if (add_enum(module, IntEnum, "BrushType",
                 brush_type_members, N_MEMBERS(brush_type_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "LineCap",
                 line_cap_members, N_MEMBERS(line_cap_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "LineJoin",
                 line_join_members, N_MEMBERS(line_join_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "FillMode",
                 fill_mode_members, N_MEMBERS(fill_mode_members)) < 0) return -1;
    if (add_enum(module, IntEnum, "TextAlign",
                 text_align_members, N_MEMBERS(text_align_members)) < 0) return -1;
    return 0;
}
