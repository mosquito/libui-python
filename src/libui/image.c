/*
 * image.c — Image type wrapping uiImage.
 */
#include "module.h"

typedef struct {
    PyObject_HEAD
    uiImage *image;
} UiImageObject;

static int
Image_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"width", "height", NULL};
    double width, height;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "dd", kwlist, &width, &height))
        return -1;

    UiImageObject *img = (UiImageObject *)self;
    img->image = uiNewImage(width, height);
    if (img->image == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "uiNewImage failed");
        return -1;
    }
    return 0;
}

static PyObject *
Image_append(PyObject *self, PyObject *args)
{
    Py_buffer buf;
    int pixel_width, pixel_height, byte_stride;
    if (!PyArg_ParseTuple(args, "y*iii", &buf, &pixel_width, &pixel_height, &byte_stride))
        return NULL;

    UiImageObject *img = (UiImageObject *)self;
    if (img->image == NULL) {
        PyBuffer_Release(&buf);
        PyErr_SetString(PyExc_RuntimeError, "image has been freed");
        return NULL;
    }

    if (buf.len < (Py_ssize_t)byte_stride * pixel_height) {
        PyBuffer_Release(&buf);
        PyErr_SetString(PyExc_ValueError, "buffer too small for given dimensions");
        return NULL;
    }

    uiImageAppend(img->image, buf.buf, pixel_width, pixel_height, byte_stride);
    PyBuffer_Release(&buf);
    Py_RETURN_NONE;
}

static int
Image_traverse(PyObject *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static int
Image_clear(PyObject *self)
{
    return 0;
}

static void
Image_dealloc(PyObject *self)
{
    UiImageObject *img = (UiImageObject *)self;
    PyObject_GC_UnTrack(self);
    if (img->image != NULL) {
        uiFreeImage(img->image);
        img->image = NULL;
    }
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyMethodDef Image_methods[] = {
    {"append", Image_append, METH_VARARGS, "append(pixels, pixel_width, pixel_height, byte_stride)\n--\n\nAppend a pixel representation (RGBA premultiplied, bytes)."},
    {NULL}
};

static PyType_Slot Image_slots[] = {
    {Py_tp_doc,       "Image(width, height)\n--\n\nAn image for use in tables."},
    {Py_tp_init,      Image_init},
    {Py_tp_methods,   Image_methods},
    {Py_tp_dealloc,   Image_dealloc},
    {Py_tp_traverse,  Image_traverse},
    {Py_tp_clear,     Image_clear},
    {0, NULL}
};

PyType_Spec Image_spec = {
    .name      = "libui.core.Image",
    .basicsize = sizeof(UiImageObject),
    .flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots     = Image_slots,
};
