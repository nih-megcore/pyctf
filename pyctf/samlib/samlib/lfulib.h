#ifndef LFU_H
#define LFU_H

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <gsl/gsl_vector.h>
#include <gsl/gsl_matrix.h>
#include <gsl/gsl_blas.h>
#include <gsl/gsl_sf_legendre.h>
#include <geoms.h>
#include <voxel.h>
#include <mesh.h>
#include <coreg.h>
#include <DataFiles.h>
#include "samutil.h"
#include "sam_param.h"

#define MU0_4PI     1.0e-07
#define TINY        1.0e-20
#define INFLATE     0.005           // 5 mm inflation
#define SWAP(a,b)   {double temp=(a);(a)=(b);(b)=temp;}

// 'HULL' -- cortical hull structure (vertices & their normals)
typedef struct {
    FIELD   *vertex;        // vertex[nv] -- coordinate & normal vector of each vertex
    FIELD   *infvertex;     // infvertex[nv] -- inflated hull for Nolte
    int     nv;             // number of vertices
    double  Vo[3];          // hull origin
    double  scale;          // approximate radius of hull
} HULL;

// integration point structure
//typedef struct {
//    FIELD   Vi;             // position & orientation
//    double  Bi[3];          // forward solutions for each cardinal moment
//} INT_PNT;

// array of N lead-field structure
typedef struct {
    gsl_matrix  *L;         // Mx3 lead-field for one of N targets
} N_LEADFIELD;

typedef struct {
    int     C;                  // number of coils
    int     S;                  // number of integration points
    FIELD   *detector;          // detector[S] -- integration points
    double  **coeffs;           // coeffs[BASIS][S] -- correction coefficients
} COEFFS;

// global variables
extern int CoeffFlag;       // flag for computing coefficients -- needed for changes in head frame
extern int ORDER;           // integration order for Nolte solutions

// subroutines
double  Berg(FIELD *Q, double r[3]);
void    DIPLeadField(double Vc[3], gsl_matrix *L, gsl_matrix *Lr, HeaderInfo *Header, ChannelInfo *Channel, int IntOrder);
void    ECDIntPnt(HeaderInfo *, ChannelInfo *, HULL *, COEFFS *);
void    ECDIntPntFree(COEFFS *d);
void    ECDLeadField(double *, gsl_matrix *, gsl_matrix *, HeaderInfo *, ChannelInfo *, HULL *, COEFFS *);
void    SolveFwd(VOXELINFO *Voxel, gsl_vector *Bc, gsl_vector *Bu, gsl_vector *Br, gsl_matrix *Cinv, HeaderInfo *Header, ChannelInfo *Channel, HULL *Hull, double *span, COEFFS *);
double  FwdSensor(FIELD *Q, SENSOR *Sensor, int Order);
void    FwdSensIntPnt(SENSOR *Sensor, int Order);
void    GetBasis(double Vc[3], double scale, double **gradbasis);
void    GetCoeffs(FIELD *detector, int nchan, HULL *Hull, double **coeffs);
void    GetHull(char *hullName, HULL *Hull);
void    GetPatchVertices(VOXELINFO *Vertex, int NumVert, double *Vcentroid, double Extent, int *NumUsed, int Solve);
void    LUsolve(double **A, double *da, int N);
void    NLeadField(VOXELINFO *Voxel, N_LEADFIELD *Lfld, HeaderInfo *Header, ChannelInfo *Channel, HULL *Hull, int N, int Model);
void    NSolve3D(double **Org, double **W, gsl_matrix *Cs, gsl_matrix *Co, HeaderInfo *Header, ChannelInfo *Channel, int N, double *span);
void    NSolveMoments(gsl_matrix *Vec, gsl_matrix *Cinv, N_LEADFIELD *L, int N, double *span);
void    NSolveFwd(VOXELINFO *Voxel, gsl_matrix *B, N_LEADFIELD *L, gsl_matrix *C, int N);
void    NSolveWts(gsl_matrix *W, gsl_matrix *B, gsl_matrix *C);
void    ROISolveFwd(VOXELINFO *ROI, int NumVertices, gsl_vector *B, gsl_matrix *Cs, gsl_matrix *Co, HeaderInfo *Header, ChannelInfo *Channel, HULL *Hull, int *Rank, int Solve);
void    ROISolveWts(VOXELINFO *ROI, int NumVertices, gsl_vector *W, gsl_matrix *Cs, gsl_matrix *Co, HeaderInfo *Header, ChannelInfo *Channel, HULL *Hull, int *Rank, int Solve);
void    ROISolveWtsLV(VOXELINFO *ROI, int NumVertices, gsl_vector *W, gsl_matrix *Cs, gsl_matrix *Co, HeaderInfo *Header, ChannelInfo *Channel, HULL *Hull, int *Rank, int Solve);
void    RandomMesh(VOXELINFO *Vertex, PARMINFO *, MESHINFO *Mesh, int N);
void    RandomVertices(VOXELINFO *Vertex, VOXELINFO *VertList, int N);
void    SelectMesh(VOXELINFO *Vertex, MESHINFO *Mesh, int N, gsl_matrix *C, HeaderInfo *Header, ChannelInfo *Channel, HULL *Hull);
void    SolveMoment(gsl_matrix *Cinv, gsl_matrix *L, double *Vec, double *span);
void    rnynm(double Vs[3], double ***fabrnm, double ***fabinm);
void    xbd(double r[3], double rt[3], double bd[3][3]);

#endif
