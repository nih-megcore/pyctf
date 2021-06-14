// coreg.h -- tuneable parameters for SAMcoreg & associated subroutines
//
//  Author: Stephen E. Robinson
//          MEG Core Facility
//          NIMH
//

#ifndef COR_H
#define COR_H

#include <math.h>

// coregistration parameters
#define DEFAULT_ORDER   10          // default order for Nolte spherical harmonics
#define MIN_Z           0.05        // z=5 cm minimum for inclusive mesh elements
#define MIN_SNR         .25         // minimum S/N
#define MAX_ANGLE       (M_PI / 3.) // maximum angular error
#define MAX_VERTEX      5000        // sample 5000 random mesh vertices from Freesurfer segmentation
#define MAX_DOT         0.80        // maximum dot product for finding sulcal vertices
#define SMIDGE          1.0e-09     // add 1 nanometre to stopping value to succeed loop test
#define INIT_TRANS      0.005       // initial translation step-size
#define INIT_ROTAT      0.005       // initial rotation step-size
#define END_TRANS       0.0001      // stopping translations step-size
#define END_ROTAT       0.0001      // stopping rotation step-size

#endif
