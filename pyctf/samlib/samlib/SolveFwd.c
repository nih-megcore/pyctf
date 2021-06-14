// SolveFwd() - solve for constrained & unconstrained forward solutions
//  plus unconstrained moment vector
//
//  Author: Stephen E. Robinson
//          MEG Core Facility
//          NIMH
//

#include <stdlib.h>
#include <lfulib.h>
#include <samlib.h>
#include <siglib.h>
#include <math.h>
#include <voxel.h>

#define QV      3           // 3 dipole moment solution

// Bc can be NULL if no constrained solution is needed
// Bu can be NULL if no unconstrained solution is needed
// if coeffs is NULL, use the MultiSphere solution, else Nolte

void SolveFwd(
    VOXELINFO   *Voxel,     // dipole position, orientation, & flags
    gsl_vector  *Bc,        // M anatomically constrained forward solution
    gsl_vector  *Bu,        // M unconstrained forward solution
    gsl_vector  *Br,        // R reference channel forward solution or NULL
    gsl_matrix  *Cinv,      // MxM inverse covariance matrix
    HeaderInfo  *Header,    // header information with sensor list
    ChannelInfo *Channel,   // sensor information
    HULL        *Hull,      // cortical hull model
    double      *span,      // eigenvalue span of 3x3 solution (return value)
    COEFFS      *coeff      // COEFFS
) {
    gsl_matrix  *L;         // MxQV primary sensor lead field
    gsl_matrix  *Lr;        // RxQV reference sensor lead field
    double      Vec[QV];    // moment vector
    double      tmp;        // accumulator
    int         i, j;       // indices
    int         M;          // primary sensor rank
    int         R;          // # of refs

    // allocate memory
    M = Header->NumPri;
    R = Header->NumRef;
    L = gsl_matrix_alloc(M, QV);
    Lr = NULL;
    if (Br) {
        Lr = gsl_matrix_alloc(R, QV);
    }

    // compute ECD lead field matrix for unit (1. A-m) dipole in each cardinal axis

    if (coeff) {
        ECDLeadField(Voxel->p, L, Lr, Header, Channel, Hull, coeff);
    } else {
        DIPLeadField(Voxel->p, L, Lr, Header, Channel, ORDER);
    }

    // compute constrained forward solution
    // using passed orientation
    if (Bc) {
        for (i=0; i<M; i++) {
            for (j=0, tmp=0.; j<QV; j++)
                tmp += Voxel->v[j] * gsl_matrix_get(L, i, j);
            gsl_vector_set(Bc, i, tmp);
        }
    }

    // If we were passed an orientation, use that to compute the refs
    if (Bc && Br) {
        for (i=0; i<R; i++) {
            for (j=0, tmp=0.; j<QV; j++)
                tmp += Voxel->v[j] * gsl_matrix_get(Lr, i, j);
            gsl_vector_set(Br, i, tmp);
        }
        Br = NULL;
    }

    if (Bu) {
        // solve generalized eigensystem for unconstrained moment vector
        SolveMoment(Cinv, L, Vec, span);
        for (i=0; i<QV; i++)
            Voxel->v[i] = Vec[i];       // make sure to return unconstrained moment vector!

        // compute unconstrained forward solution
        for (i=0; i<M; i++) {
            for (j=0, tmp=0.; j<QV; j++)
                tmp += Voxel->v[j] * gsl_matrix_get(L, i, j);
            gsl_vector_set(Bu, i, tmp);
        }
    }

    if (Bu && Br) {
        for (i=0; i<R; i++) {
            for (j=0, tmp=0.; j<QV; j++)
                tmp += Voxel->v[j] * gsl_matrix_get(Lr, i, j);
            gsl_vector_set(Br, i, tmp);
        }
    }

    gsl_matrix_free(L);
    gsl_matrix_free(Lr);
}
