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
******************************************************************************/

#include <stdio.h>
#include <gmp.h>

struct mpz_bin_struct {
    mpz_t i;
    unsigned len;
};

typedef struct mpz_bin_struct mpz_bin;

mpz_bin mpz_bin_d (mpz_bin x);

mpz_bin mpz_bin_d_k (mpz_bin x, unsigned k);

double bien(mpz_bin s);
double tbien(mpz_bin s);
