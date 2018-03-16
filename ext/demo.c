/******************************************************************************
* Copyright 2018 National Technology & Engineering Solutions of Sandia, LLC
* (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
* Government retains certain rights in this software.
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
* ---
*
* This file is a demonstration of the use of the C implementations from a
* native C program.
*
* To build this file, see the 'c_demo' rule in the Makefile.
******************************************************************************/

#include <stdio.h>
#include <gmp.h>
#include <math.h>

#include "bientropy.h"

int main (void) {
    int final_result = 0;
    mpz_t integ;
    mpz_init (integ);

    mpz_set_ui(integ, 0x01);

#ifdef DEBUG
    gmp_printf("Integer: %Zd\n", integ);
#endif
    mpz_clear(integ);

    mpz_bin b;
    mpz_init(b.i);

    unsigned inputs[] = {0x0,  0x1,  0x2,  0x3,
                         0x0,  0x3,  0x1,  0x2,
                         0xc,  0xf,  0xd,  0xe,
                         0x4,  0x7,  0x5,  0x6,
                         0x8,  0xb,  0x9,  0xa,
                         0x00, 0x0f, 0x05, 0x0a};

    double biens[] = {0.0,   1.0,   1.0,   0.0,
                      0.000, 0.405, 0.950, 0.950,
                      0.405, 0.000, 0.950, 0.950,
                      0.950, 0.950, 0.143, 0.405,
                      0.950, 0.950, 0.405, 0.143,
                      0.000, 0.107, 0.230, 0.230};

    double tbiens[] = {0.0,   1.0,   1.0,   0.0,
                       0.000, 0.536, 0.931, 0.931,
                       0.536, 0.000, 0.931, 0.931,
                       0.931, 0.931, 0.218, 0.536,
                       0.931, 0.931, 0.536, 0.218,
                       0.000, 0.394, 0.556, 0.556};

    unsigned lens[] = {2, 2, 2, 2,
                       4, 4, 4, 4,
                       4, 4, 4, 4,
                       4, 4, 4, 4,
                       4, 4, 4, 4,
                       8, 8, 8, 8};

    unsigned int i;
    for (i = 0; i < sizeof(inputs)/sizeof(unsigned); i++)
    {
        mpz_set_ui(b.i, inputs[i]);
        b.len = lens[i];
        double result = bien(b);
        printf("BiEn(%x) = %.2f, should be %.2f",
            inputs[i], result, biens[i]);
        if (round(result*100) == round(biens[i]*100)) {
            printf(" PASS\n");
        } else {
            final_result |= 1;
            printf(" FAIL\n");
        }
#ifdef DEBUG
        gmp_printf("Bin Deriv.: %Zx\n", mpz_bin_d(b).i);
        gmp_printf("BiEn(%Zx): %f\n", integ, bien(integ, 2));
#endif
        result = tbien(b);
        printf("TBiEn(%x) = %.2f, should be %.2f",
            inputs[i], result, tbiens[i]);
        if (round(result*100) == round(tbiens[i]*100)) {
            printf(" PASS\n");
        } else {
            final_result |= 2;
            printf(" FAIL\n");
        }
    }

    mpz_clear(b.i);

    if (!final_result) {
        printf("All tests OK\n");
    } else {
        printf("At least one test FAILED\n");
    }

    return final_result;
}
