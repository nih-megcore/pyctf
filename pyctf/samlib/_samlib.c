/* Level 1 API to samlib. */

/* Some potential issues.
Only one dataset can be open at a time.
Static variables must go away.
The dataset must first be opened with pyctf.dsopen().
*/

/* As the level 2 API evolves, this interface will probably change. */

#include <Python.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <arrayobject.h>

#include <unistd.h>
#include <float.h>
#include <strings.h>
#include <fcntl.h>

#include "geoms.h"
#include "samlib.h"
#include "siglib.h"
#include "lfulib.h"
#include "DataFiles.h"
#include "SAMfiles.h"
#include "samutil.h"

#include <gsl/gsl_matrix.h>

// ugly static mess - these flags indicate which things have been initialized
// eventually this will be wrapped into a struct/capsule object

static int HaveHeader = FALSE;
static int HaveModel = -1;  // MSPHERE or NOLTE
static int HaveHull = FALSE;
static int HaveHDM = FALSE;
static int HaveIntPnt = FALSE;
static int HaveAtlas = FALSE;

static HeaderInfo Header;   /* there can be only one */
static ChannelInfo *Channel;
static EpochInfo *Epoch;
static int M;
//static gsl_matrix *L;
static COEFFS *Coeffs;
static HULL Hull;
static HEAD_MODEL Model;
static VOXELINFO *Voxel;
static int V;
static GIIATLAS *GAtlas;

#define MORDER 3            // default integration order for multisphere
#define NORDER 10           // default integration order for Nolte

static char Doc_GetDsInfo[] = "GetDsInfo(ds)\n\
Read the dataset's header information.\n";

/* GetDsInfo(ds) needs to be called first. */

static PyObject *GetDsInfo_wrap(PyObject *self, PyObject *args)
{
    PyObject *o, *ds;
    int i;
    char *dsname, *setname;

    /* First argument is the ds object. */

    if (!PyArg_ParseTuple(args, "O", &ds)) {
        return NULL;
    }

    /* Get ds.dsname and ds.setname */

    o = PyObject_GetAttrString(ds, "dsname");
    if (o == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "[GetDsInfo] no dsname; pass the result of pyctf.dsopen()");
        return NULL;
    }
    dsname = copy_string((char *)PyUnicode_AsUTF8(o));
    Py_DECREF(o);

    o = PyObject_GetAttrString(ds, "setname");
    if (o == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "[GetDsInfo] no setname!");
        free(dsname);
        return NULL;
    }
    setname = copy_string((char *)PyUnicode_AsUTF8(o));
    Py_DECREF(o);

    GetDsInfo(dsname, setname, &Header, &Channel, &Epoch, NULL, TRUE);

    free(dsname);
    free(setname);

    /* Set some other global variables. */

    HaveHeader = TRUE;
    M = Header.NumPri;
    //L = gsl_matrix_alloc(M, 3);
    Coeffs = new(COEFFS);

    Py_INCREF(Py_None);
    return Py_None;
}

static void nods_err()
{
    PyErr_SetString(PyExc_RuntimeError, "[samlib] you must call GetDsInfo first.");
}
#define CHECKH() if (!HaveHeader) { nods_err(); return NULL; }

static char Doc_SetModel[] = "SetModel(m)\n\
m must be either 'MultiSphere' or 'Nolte'.\n";

static PyObject *SetModel_wrap(PyObject *self, PyObject *args)
{
    char *s;

    CHECKH();

    if (!PyArg_ParseTuple(args, "s", &s)) {
        return NULL;
    }

    if (strcmp(s, "MultiSphere") == 0) {
        HaveModel = MSPHERE;
    } else if (strcmp(s, "Nolte") == 0) {
        HaveModel = NOLTE;
    } else {
        PyErr_SetString(PyExc_RuntimeError, "[SetModel] model must be either 'MultiSphere' or 'Nolte'.");
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static char Doc_GetMRIPath[] = "path = GetMRIPath(param, name)\n\
Return a pathname constructed using the MRIPattern, parameters in param, and name.\n";

static PyObject *GetMRIPath_wrap(PyObject *self, PyObject *args)
{
    char *name, path[256];
    PyObject *o, *p;

    if (!PyArg_ParseTuple(args, "Os", &p, &name)) {
        return NULL;
    }

    if (!GetMRIPath(path, sizeof(path), p, name)) {
        return NULL;
    }
    return Py_BuildValue("s", path);
}

static char Doc_GetFilePath[] = "path = GetFilePath(pattern, param, name)\n\
Return a pathname constructed using the pattern, using parameters in param, and name.\n";

static PyObject *GetFilePath_wrap(PyObject *self, PyObject *args)
{
    char *pattern, *name, path[256];
    PyObject *o, *p;

    if (!PyArg_ParseTuple(args, "sOs", &pattern, &p, &name)) {
        return NULL;
    }

    if (!GetFilePath(pattern, path, sizeof(path), p, name)) {
        return NULL;
    }
    return Py_BuildValue("s", path);
}

/* utility functions to get p.attributes for various types */

int param_getstr(PyObject *p, char *name, char **s)
{
    char msg[100];
    PyObject *o;

    o = PyObject_GetAttrString(p, name);
    if (o == NULL || o == Py_None) {
        snprintf(msg, sizeof(msg), "Parameter %s must be set.", name);
        PyErr_SetString(PyExc_RuntimeError, msg);
        return FALSE;
    }
    *s = copy_string((char *)PyUnicode_AsUTF8(o));

    Py_DECREF(o);

    return TRUE;
}

int param_getint(PyObject *p, char *name, int *i)
{
    char msg[100];
    PyObject *o;

    o = PyObject_GetAttrString(p, name);
    if (o == NULL || o == Py_None) {
        snprintf(msg, sizeof(msg), "Parameter %s must be set.", name);
        PyErr_SetString(PyExc_RuntimeError, msg);
        return FALSE;
    }
    *i = (int)PyLong_AsLong(o);
    Py_DECREF(o);

    return TRUE;
}

static char Doc_GetHull[] = "GetHull([name])\n\
Read in a hull model file (default \"hull.shape\" in the dataset).\n";

static PyObject *GetHull_wrap(PyObject *self, PyObject *args)
{
    int i;
    char *path, *dsname, *name;

    CHECKH();

    /* hullname argument is optional. default to hull.shape in the dataset. */

    name = NULL;
    PyArg_ParseTuple(args, "|s", &name);
    if (name == NULL) {
        name = "hull.shape";
        dsname = Header.DsName;
        i = strlen(dsname) + 1 + strlen(name);
        path = new_string(i);
        sprintf(path, "%s/%s", Header.DsName, name);
        GetHull(path, &Hull);
        free(path);
    } else {
        GetHull(name, &Hull);
    }

    HaveHull = TRUE;

    Py_INCREF(Py_None);
    return Py_None;
}

static char Doc_GetHDM[] = "GetHDM([name])\n\
Read in a multisphere model file (default \"default.hdm\" in the dataset).\n";

static PyObject *GetHDM_wrap(PyObject *self, PyObject *args)
{
    int i, j, k, S, v;
    char *path, *dsname, *name;

    CHECKH();

    /* hdmname argument is optional. default to default.hdm in the dataset.*/

    name = NULL;
    PyArg_ParseTuple(args, "|s", &name);
    if (name == NULL) {
        name = "default.hdm";
        dsname = Header.DsName;
        i = strlen(dsname) + 1 + strlen(name);
        path = new_string(i);
        sprintf(path, "%s/%s", Header.DsName, name);
        GetHDM(path, &Model);
        free(path);
    } else {
        GetHDM(name, &Model);
    }

    /* Set the LocalSphere origins from the model. */

    S = Header.NumPri + Header.NumRef;
    for (i = 0; i < S; i++) {
        k = strlen(Model.MultiSphere[i].ChanName) - 1;
        for (j = 0; j < Header.NumChannels; j++) {
            if (!strncmp(Model.MultiSphere[i].ChanName, Channel[j].ChannelName, k)) {
                for (v = X_; v <= Z_; v++) {
                    Channel[j].Geom.MEGSensor.LocalSphere[v] = Model.MultiSphere[i].Origin[v];
                }
                break;
            }
        }
    }

    HaveHDM = TRUE;

    Py_INCREF(Py_None);
    return Py_None;
}

static char Doc_GetVoxels[] = "GetVoxels(xbounds, ybounds, zbounds, stepsize)\n\
Generate an ROI array. The bounds are tuples, and all values are in cm.\n";

static PyObject *GetVoxels_wrap(PyObject *self, PyObject *args)
{
    double s[3], e[3], step;

    CHECKH();
    if (!HaveHull) {
        PyErr_SetString(PyExc_RuntimeError, "[GetVoxels] you must call GetHull() first.");
        return NULL;
    }

    if (!PyArg_ParseTuple(args, "(dd)(dd)(dd)d", &s[0], &e[0], &s[1], &e[1], &s[2], &e[2], &step)) {
        return NULL;
    }

    GetVoxels(&Voxel, &V, &Hull, s, e, step);

    Py_INCREF(Py_None);
    return Py_None;
}

static char Doc_SetIntPnt[] = "SetIntPnt([order])\n\
Set up the forward integration points for the specified model.\n\
This must be called before calling SolveFwd().\n";

static PyObject *SetIntPnt_wrap(PyObject *self, PyObject *args)
{
    int i, j;

    CHECKH();
    if (HaveModel < 0) {
        PyErr_SetString(PyExc_RuntimeError, "[SetIntPnt] you must call SetModel() first.");
        return NULL;
    }
    if (HaveModel == MSPHERE) {
        if (!HaveHDM) {
            PyErr_SetString(PyExc_RuntimeError, "[SetIntPnt] you must call GetHDM() first.");
            return NULL;
        }
        i = MORDER;
    } else {
        if (!HaveHull) {
            PyErr_SetString(PyExc_RuntimeError, "[SetIntPnt] you must call GetHull() first.");
            return NULL;
        }
        i = NORDER;
    }

    if (!PyArg_ParseTuple(args, "|i", &i)) {
        return NULL;
    }
    ORDER = i;      // set global variable

    if (HaveModel == MSPHERE) {
        for (i = 0; i < Header.NumRef; i++) {
            j = Header.RsIndex[i];
            FwdSensIntPnt(&Channel[j].Geom.MEGSensor, ORDER);
        }
        for (i = 0; i < Header.NumPri; i++) {
            j = Header.PsIndex[i];
            FwdSensIntPnt(&Channel[j].Geom.MEGSensor, ORDER);
        }
    } else {
        ECDIntPnt(&Header, Channel, &Hull, Coeffs);
    }

    HaveIntPnt = TRUE;

    Py_INCREF(Py_None);
    return Py_None;
}

/* Create a GSL array from a numpy array. */

static gsl_matrix *Py2gsl(PyObject *o, char *name)
{
    int i, j, m;
    double *d;
    char buf[100];
    gsl_matrix *c;
    PyArrayObject *C;

    C = (PyArrayObject *)PyArray_ContiguousFromAny(o, NPY_DOUBLE, 2, 2);
    if (C == NULL) {
        return NULL;
    }

    m = PyArray_DIM(C, 0);
    if (m != PyArray_DIM(C, 1)) {
        sprintf(buf, "[samlib] %s is not a square matrix!", name);
        PyErr_SetString(PyExc_RuntimeError, buf);
        Py_DECREF(C);
        return NULL;
    }

    // copy the array @@@ it should be possible to do this without a copy

    d = (double *)PyArray_DATA(C);
    c = gsl_matrix_alloc(m, m);
    for (i = 0; i < m; i++) {
        for (j = 0; j < m; j++) {
            gsl_matrix_set(c, i, j, *d++);
        }
    }
    Py_DECREF(C);

    return c;
}

static char Doc_SolveFwd[] = "Call either as\n\
    Bc = SolveFwd(None, pos, ori)\n\
or\n\
    (Bu, v, cond) = SolveFwd(cinv, pos)\n\
or\n\
    (Bc, Bu, v, cond) = SolveFwd(cinv, pos, ori)\n\
SolveFwd() can compute both/either the constrained (Bc) and/or the\n\
unconstrained (Bu) forward solution for a dipole at pos (3-tuple, cm) with\n\
orientation ori (unit vector) using the inverse covariance matrix cinv. If\n\
cinv is not specified, only the constrained (Bc) solution is computed. If no\n\
orientation is supplied, only the unconstrained (Bu) solution is computed.\n\
You must call SetModel() first. Also, for the unconstrained solution,\n\
return v, the unconstrained moment vector, and sqrt(condition #).\n";

static PyObject *SolveFwd_wrap(PyObject *self, PyObject *args)
{
    int i, j, m;
    int oflag;
    double s, cond, *pos, *ori, *d;
    VOXELINFO vox;
    gsl_vector *bc;
    gsl_vector *bu;
    gsl_vector *br;
    gsl_matrix *cinv;
    npy_intp dim[2];
    PyObject *o, *cinvo;
    PyArrayObject *Cinv, *Bc, *Bu, *v;

    CHECKH();
    if (!HaveIntPnt) {
        PyErr_SetString(PyExc_RuntimeError, "[SolveFwd] you must call SetIntPnt() first.");
        return NULL;
    }

    pos = vox.p;
    ori = vox.v;
    ori[0] = HUGE;
    oflag = FALSE;
    if (!PyArg_ParseTuple(args, "O(ddd)|(ddd)",
            &cinvo, pos, pos + 1, pos + 2, ori, ori + 1, ori + 2)) {
        return NULL;
    }
    if (ori[0] != HUGE) {
        oflag = TRUE;
    }

    for (i = 0; i < 3; i++) {
        pos[i] *= .01;          // convert to meters
    }
    if (oflag) {                // ensure unit vector
        s = 0.;
        for (i = 0; i < 3; i++) {
            s += ori[i] * ori[i];
        }
        if (s > 0.) {
            s = sqrt(s);
            for (i = 0; i < 3; i++) {
                ori[i] /= s;
            }
        }
    }

    if (cinvo == Py_None) {
        cinv = NULL;
        if (!oflag) {
            PyErr_SetString(PyExc_RuntimeError, "[SolveFwd] you must specify an orientation.");
            return NULL;
        }
    } else {
        cinv = Py2gsl(cinvo, "cinv");
        if (cinv == NULL) {
            return NULL;
        }
    }

    m = Header.NumPri;
    bc = bu = NULL;
    Bc = Bu = NULL;
    br = NULL;
    if (oflag) {
        bc = gsl_vector_alloc(m);
    }
    if (cinv) {
        bu = gsl_vector_alloc(m);
    }

    if (HaveModel == NOLTE) {
        SolveFwd(&vox, bc, bu, br, cinv, &Header, Channel, &Hull, &cond, Coeffs);
    } else {
        SolveFwd(&vox, bc, bu, br, cinv, &Header, Channel, NULL, &cond, NULL);
    }

    if (cinv) {
        gsl_matrix_free(cinv);
    }

    /* Allocate numpy arrays for the results and fill them in. */

    if (bc) {
        dim[0] = m;
        Bc = (PyArrayObject *)PyArray_SimpleNew(1, dim, NPY_DOUBLE);
        if (Bc == NULL) {
            goto err;
        }
        d = (double *)PyArray_DATA(Bc);
        for (i = 0; i < m; i++) {
            *d++ = gsl_vector_get(bc, i);
        }
    }

    if (bu) {
        dim[0] = m;
        Bu = (PyArrayObject *)PyArray_SimpleNew(1, dim, NPY_DOUBLE);
        if (Bu == NULL) {
            goto err;
        }

        dim[0] = 3;
        v = (PyArrayObject *)PyArray_SimpleNew(1, dim, NPY_DOUBLE);
        if (v == NULL) {
            goto err;
        }

        d = (double *)PyArray_DATA(Bu);
        for (i = 0; i < m; i++) {
            *d++ = gsl_vector_get(bu, i);
        }

        d = (double *)PyArray_DATA(v);
        for (i = 0; i < 3; i++) {
            *d++ = vox.v[i];
        }
    }

    if (cinvo == Py_None) {
        gsl_vector_free(bc);
        return (PyObject *)Bc;
    }

    j = 3;
    if (bc) {
        j = 4;
    }
    o = PyTuple_New(j);
    i = 0;
    if (bc) {
        PyTuple_SET_ITEM(o, i, (PyObject *)Bc);
        i++;
    }
    if (bu) {
        PyTuple_SET_ITEM(o, i, (PyObject *)Bu);
        PyTuple_SET_ITEM(o, i + 1, (PyObject *)v);
        PyTuple_SET_ITEM(o, i + 2, PyFloat_FromDouble(cond));
    }

    if (bu) gsl_vector_free(bu);
    if (bc) gsl_vector_free(bc);

    return o;

err:
    if (bu) gsl_vector_free(bu);
    if (bc) gsl_vector_free(bc);
    if (Bu) Py_DECREF(Bu);
    if (Bc) Py_DECREF(Bc);
    return NULL;
}

static char Doc_SolveFwdRefs[] = "Call either as\n\
    Br, Bc = SolveFwdRefs(None, pos, ori)\n\
or\n\
    (Br, Bu, v, cond) = SolveFwdRefs(cinv, pos)\n\
SolveFwdRefs() is similar to SolveFwd(), but also returns\n\
Br, the references, before any others.\n";

static PyObject *SolveFwdRefs_wrap(PyObject *self, PyObject *args)
{
    int i, j, m;
    int oflag;
    double s, cond, *pos, *ori, *d;
    VOXELINFO vox;
    gsl_vector *bc;
    gsl_vector *bu;
    gsl_vector *br;
    gsl_matrix *cinv;
    npy_intp dim[2];
    PyObject *o, *cinvo;
    PyArrayObject *Cinv, *Bc, *Bu, *Br, *v;

    CHECKH();
    if (!HaveIntPnt) {
        PyErr_SetString(PyExc_RuntimeError, "[SolveFwdRefs] you must call SetIntPnt() first.");
        return NULL;
    }

    pos = vox.p;
    ori = vox.v;
    ori[0] = HUGE;
    oflag = FALSE;
    if (!PyArg_ParseTuple(args, "O(ddd)|(ddd)",
            &cinvo, pos, pos + 1, pos + 2, ori, ori + 1, ori + 2)) {
        return NULL;
    }
    if (ori[0] != HUGE) {
        oflag = TRUE;
    }

    for (i = 0; i < 3; i++) {
        pos[i] *= .01;          // convert to meters
    }
    if (oflag) {                // ensure unit vector
        s = 0.;
        for (i = 0; i < 3; i++) {
            s += ori[i] * ori[i];
        }
        if (s > 0.) {
            s = sqrt(s);
            for (i = 0; i < 3; i++) {
                ori[i] /= s;
            }
        }
    }

    if (cinvo == Py_None) {
        cinv = NULL;
        if (!oflag) {
            PyErr_SetString(PyExc_RuntimeError, "[SolveFwdRefs] you must specify an orientation.");
            return NULL;
        }
    } else {
        cinv = Py2gsl(cinvo, "cinv");
        if (cinv == NULL) {
            return NULL;
        }
    }

    m = Header.NumPri;
    bc = bu = NULL;
    Bc = Bu = NULL;
    if (oflag) {
        bc = gsl_vector_alloc(m);
    }
    if (cinv) {
        bu = gsl_vector_alloc(m);
    }
    br = gsl_vector_alloc(Header.NumRef);

    if (HaveModel == NOLTE) {
        SolveFwd(&vox, bc, bu, br, cinv, &Header, Channel, &Hull, &cond, Coeffs);
    } else {
        SolveFwd(&vox, bc, bu, br, cinv, &Header, Channel, NULL, &cond, NULL);
    }

    if (cinv) {
        gsl_matrix_free(cinv);
    }

    /* Allocate numpy arrays for the results and fill them in. */

    if (bc) {
        dim[0] = m;
        Bc = (PyArrayObject *)PyArray_SimpleNew(1, dim, NPY_DOUBLE);
        if (Bc == NULL) {
            goto err;
        }
        d = (double *)PyArray_DATA(Bc);
        for (i = 0; i < m; i++) {
            *d++ = gsl_vector_get(bc, i);
        }
    }

    if (bu) {
        dim[0] = m;
        Bu = (PyArrayObject *)PyArray_SimpleNew(1, dim, NPY_DOUBLE);
        if (Bu == NULL) {
            goto err;
        }

        dim[0] = 3;
        v = (PyArrayObject *)PyArray_SimpleNew(1, dim, NPY_DOUBLE);
        if (v == NULL) {
            goto err;
        }

        d = (double *)PyArray_DATA(Bu);
        for (i = 0; i < m; i++) {
            *d++ = gsl_vector_get(bu, i);
        }

        d = (double *)PyArray_DATA(v);
        for (i = 0; i < 3; i++) {
            *d++ = vox.v[i];
        }
    }

    m = Header.NumRef;
    dim[0] = m;
    Br = (PyArrayObject *)PyArray_SimpleNew(1, dim, NPY_DOUBLE);
    if (Br == NULL) {
        goto err;
    }
    d = (double *)PyArray_DATA(Br);
    for (i = 0; i < m; i++) {
        *d++ = gsl_vector_get(br, i);
    }
    gsl_vector_free(br);
    br = NULL;

    if (cinvo == Py_None) {
        gsl_vector_free(bc);
        o = PyTuple_New(2);
        PyTuple_SET_ITEM(o, 0, (PyObject *)Br);
        PyTuple_SET_ITEM(o, 1, (PyObject *)Bc);
        return o;
    }

    j = 1;
    if (bc) {
        j++;
    }
    if (bu) {
        j += 3;
    }
    o = PyTuple_New(j);
    PyTuple_SET_ITEM(o, 0, (PyObject *)Br);
    i = 1;
    if (bc) {
        PyTuple_SET_ITEM(o, i, (PyObject *)Bc);
        i++;
    }
    if (bu) {
        PyTuple_SET_ITEM(o, i, (PyObject *)Bu);
        PyTuple_SET_ITEM(o, i + 1, (PyObject *)v);
        PyTuple_SET_ITEM(o, i + 2, PyFloat_FromDouble(cond));
    }

    if (bu) gsl_vector_free(bu);
    if (bc) gsl_vector_free(bc);

    return o;

err:
    if (bu) gsl_vector_free(bu);
    if (bc) gsl_vector_free(bc);
    if (br) gsl_vector_free(br);
    if (Bu) Py_DECREF(Bu);
    if (Bc) Py_DECREF(Bc);
    if (Br) Py_DECREF(Br);
    return NULL;
}

static char Doc_SAMsolve[] = "w, s2, n2 = SAMsolve(c, cinv, B, nse)\n\
Given a covariance matrix, its inverse, a forward solution B, and the mean\n\
sensor noise (nse), compute beamformer weights (w), output power (s2) and\n\
noise (n2) estimates.\n";

static PyObject *SAMsolve_wrap(PyObject *self, PyObject *args)
{
    int i, m;
    double nse, s2, n2, *d;
    gsl_vector *b, *w;
    gsl_matrix *c, *cinv;
    npy_intp dim[1];
    PyObject *o, *co, *cinvo, *Bo;
    PyArrayObject *B, *W;

    CHECKH();
    m = Header.NumPri;

    if (!PyArg_ParseTuple(args, "OOOd", &co, &cinvo, &Bo, &nse)) {
        return NULL;
    }

    b = w = NULL;

    // copy numpy arrays to gsl arrays

    c = Py2gsl(co, "c");
    if (c == NULL) {
        return NULL;
    }
    cinv = Py2gsl(cinvo, "cinv");
    if (cinv == NULL) {
        goto err;
    }

    // and the forward solution vector

    B = (PyArrayObject *)PyArray_ContiguousFromAny(Bo, NPY_DOUBLE, 1, 1);
    if (B == NULL) {
        goto err;
    }
    d = (double *)PyArray_DATA(B);
    b = gsl_vector_alloc(m);
    for (i = 0; i < m; i++) {
        gsl_vector_set(b, i, *d++);
    }
    Py_DECREF(B);

    // return the weights in an array

    dim[0] = m;
    W = (PyArrayObject *)PyArray_SimpleNew(1, dim, NPY_DOUBLE);
    if (W == NULL) {
        goto err;
    }
    w = gsl_vector_alloc(m);

    SAMsolve(c, cinv, b, w, nse, &s2, &n2);

    // copy the weights

    d = (double *)PyArray_DATA(W);
    for (i = 0; i < m; i++) {
        *d++ = gsl_vector_get(w, i);
    }

    gsl_vector_free(w);
    gsl_vector_free(b);
    gsl_matrix_free(cinv);
    gsl_matrix_free(c);

    // create output tuple

    o = PyTuple_New(3);
    PyTuple_SET_ITEM(o, 0, (PyObject *)W);
    PyTuple_SET_ITEM(o, 1, PyFloat_FromDouble(s2));
    PyTuple_SET_ITEM(o, 2, PyFloat_FromDouble(n2));

    return o;

err:
    if (b) gsl_vector_free(b);
    if (cinv) gsl_matrix_free(cinv);
    if (c) gsl_matrix_free(c);
    return NULL;
}

static char Doc_GetGiiAtlas[] = "GetGiiAtlas(name)\n\
Read a GIFTI atlas file, produced by mkGiiAtlas.\n";

static PyObject *GetGiiAtlas_wrap(PyObject *self, PyObject *args)
{
    char *name;

    CHECKH();

    if (!PyArg_ParseTuple(args, "s", &name)) {
        return NULL;
    }

    GAtlas = GetGiiAtlas(name);             // @@@ no error return, just exits on error

    Py_INCREF(Py_None);
    return Py_None;
}

#if 0
static char Doc_X[] = "X()\n\
.\n";

static PyObject *X_wrap(PyObject *self, PyObject *args)
{
    PyObject *o;
    PyArrayObject *r;

    CHECKH();

    if (!PyArg_ParseTuple(args, "O", &o)) {
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}
#endif

static char Doc__samlib[] = "Low level access to the Synthetic Aperture Magnetometry library.";

static PyMethodDef Methods[] = {
    { "GetDsInfo", GetDsInfo_wrap, METH_VARARGS, Doc_GetDsInfo },
    { "SetModel", SetModel_wrap, METH_VARARGS, Doc_SetModel },
    { "GetMRIPath", GetMRIPath_wrap, METH_VARARGS, Doc_GetMRIPath },
    { "GetFilePath", GetFilePath_wrap, METH_VARARGS, Doc_GetFilePath },
    { "GetHull", GetHull_wrap, METH_VARARGS, Doc_GetHull },
    { "GetHDM", GetHDM_wrap, METH_VARARGS, Doc_GetHDM },
    { "GetVoxels", GetVoxels_wrap, METH_VARARGS, Doc_GetVoxels },
    { "SetIntPnt", SetIntPnt_wrap, METH_VARARGS, Doc_SetIntPnt },
    { "SolveFwd", SolveFwd_wrap, METH_VARARGS, Doc_SolveFwd },
    { "SolveFwdRefs", SolveFwdRefs_wrap, METH_VARARGS, Doc_SolveFwdRefs },
    { "SAMsolve", SAMsolve_wrap, METH_VARARGS, Doc_SAMsolve },
    { "GetGiiAtlas", GetGiiAtlas_wrap, METH_VARARGS, Doc_GetGiiAtlas },
//    { "X", X_wrap, METH_VARARGS, Doc_X },
    { NULL, NULL, 0, NULL }
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_samlib",
    Doc__samlib,
    -1,
    Methods,
    NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC PyInit__samlib(void)
{
    PyObject *m;

    m = PyModule_Create(&moduledef);
    if (m == NULL) {
        return NULL;
    }

    import_array();

    return m;
}

#else

PyMODINIT_FUNC init_samlib()
{
    Py_InitModule3("_samlib", Methods, Doc__samlib);
    import_array();
}

#endif
