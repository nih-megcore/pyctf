// CtoSl() -- convert cartesian to spherical coordinates
//
// enter with x, y, and z
//
// exit with radius 'rho' in units of x, y, and z
// and spherical angles theta and phi
//
//  Author: Stephen E. Robinson
//          MEG Core Facility
//          NIMH
//

#include <math.h>
#include <geoms.h>

void CtoS(
    double  *c,     // Cartesian vector
    double  *s      // spherical vector
) {
    double  S;

    s[RHO_] = sqrt(c[X_] * c[X_] + c[Y_] * c[Y_] + c[Z_] * c[Z_]) + 1.0e-18;
    S = c[Z_] / s[RHO_];
    if (fabs(S) <= 1.)              // -1 <= S <= +1
        s[THETA_] = acos(S);        // 0 <= theta <= π
    else
        s[THETA_] = 0.;
    S = c[Y_] / sqrt(c[X_] * c[X_] + c[Y_] * c[Y_]);
    if (fabs(S) > 1.) {             // -1 <= S <= +1
        if (S >= 0.)
            S = 1.;
        else
            S = -1.;
    }
    if (c[X_] >= 0.)
        s[PHI_] = asin(S);          // -π/2 <= phi <= +π/2
    else
        s[PHI_] = M_PI - asin(S);
}
