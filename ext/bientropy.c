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
* This file implements the BiEn and TBiEn metrics in C using the GNU Multiple
* Precision Library (GMP).
******************************************************************************/

#include <stdio.h>
#include <gmp.h>
#include <math.h>

#include "bientropy.h"

/** brief mpz_bin_d - The binary derivative is computed using the exclusive or
 * (XOR) of all adjacent bit positions in a bitstring.
 *
 * param x mpz_bin the input bitstring with length n
 *
 * return mpz_bin the binary derivative of the input bitstring with length n-1
 */
mpz_bin mpz_bin_d (mpz_bin x)
{
    mpz_bin r;
    mpz_init(r.i);

    mpz_t a, b;
    mpz_init(a);
    mpz_init(b);

#ifdef DEBUG
    gmp_printf("x.i: %Zx\n", x.i);
#endif
    mpz_set(a, x.i);
    mpz_set(b, x.i);
    mpz_clrbit(a, x.len-1);
#ifdef DEBUG
    gmp_printf("a: %Zx\n", a);
#endif
    mpz_tdiv_q_2exp(b, b, 1);
#ifdef DEBUG
    gmp_printf("b: %Zx\n", b);
#endif
    mpz_xor(r.i, a, b);
    r.len = x.len-1;
#ifdef DEBUG
    gmp_printf("bin deriv: %Zx, %d bits\n", r.i, r.len);
#endif

    mpz_clear(a);
    mpz_clear(b);

    return (r);
}

/** brief mpz_bin_d_k - Return the kth binary derivative of the string 'bits'
 *
 * param x mpz_bin the input bitstring with length n
 * param k unsigned the number of repeated binary derivatives
 * return mpz_bin the kth binary derivative of length n-k where n is the length
 * of the input
 *
 */
mpz_bin mpz_bin_d_k (mpz_bin x, unsigned k)
{
    if (k == 0) {
        return x;
    } else {
        return mpz_bin_d(mpz_bin_d_k(x, k-1));
    }
}

/** brief bien - BiEntropy, or BiEn for short, is a weighted average of the
 * Shannon binary entropies of the string and the first n-2 binary derivatives
 * of the string using a simple power law. This version of BiEntropy is
 * suitable for shorter binary strings where n <= 32, approximately.
 *
 * param s mpz_bin the input bitstring on which to operate
 * return double the BiEntropy of the input
 *
 */
double bien(mpz_bin s)
{
    mpf_t t, t_k;
    mpf_init (t);
    mpf_init (t_k);
    mpz_bin s_k, s_k_new;
    mpz_init (s_k.i);
    mpz_set(s_k.i, s.i);
    s_k.len = s.len;
    unsigned ones;
    double p, e, g;

    unsigned k;
    for (k = 0; k<s.len - 1; k++)
    {
        ones = mpz_popcount(s_k.i);
        p = ((double)ones)/s_k.len;
        if (p == 0) {
            e = 0.0;
        } else {
            e = -p*log2(p);
        }
        if (p == 1) {
            g = 0.0;
        } else {
            g = -1*(1-p)*log2(1-p);
        }
        mpf_set_d(t_k, e + g);
#ifdef DEBUG
        gmp_printf("t_k= e + g= %Ff\n", t_k);
#endif
        mpf_mul_2exp(t_k, t_k, k);
#ifdef DEBUG
        gmp_printf("k= %d, t_k= t_k * 2^k= %Ff\n", k, t_k);

        gmp_printf("%Zx %d %d %.2f %.2f %.2f %.2f %.2f %d %d %.2Ff\n",
                s_k.i, ones, s_k.len, p, 1-p, e, g, e + g, k, 1<<k, t_k);
#endif

        mpf_add(t, t, t_k);
        s_k_new = mpz_bin_d(s_k);
        mpz_set(s_k.i, s_k_new.i);
        s_k.len = s_k_new.len;
        mpz_clear(s_k_new.i);
    }

    mpf_t result;
    mpf_init(result);
    mpf_set_ui(result, 1);
    mpf_mul_2exp(result, result, s.len-1);
    mpf_sub_ui(result, result, 1);
    mpf_ui_div(result, 1, result);
    mpf_mul(result, result, t);
    double retval = mpf_get_d(result);
    mpf_clear(result);

    mpf_clear(t);
    mpf_clear(t_k);
    mpz_clear(s_k.i);

    return (retval);
}

/** brief TBiEn - The logarithmic weighting BiEntropy, or TBiEn for short,
 * gives greater weight to the higher binary derivatives. As a result, has a
 * slightly faster runtime because the weights tend to be smaller than for
 * BiEn.
 *
 * param s mpz_bin the input bitstring on which to operate
 * return double the TBiEntropy of the input
 *
 */
double tbien(mpz_bin s)
{
    mpf_t t, t_k, l, l_k;
    mpf_init (t);
    mpf_init (t_k);
    mpf_init (l);
    mpf_init (l_k);
    mpz_bin s_k, s_k_new;
    mpz_init (s_k.i);
    mpz_set(s_k.i, s.i);
    s_k.len = s.len;
    unsigned ones;
    double p, e, g;

    unsigned k;
    for (k = 0; k<s.len - 1; k++)
    {
        ones = mpz_popcount(s_k.i);
        p = ((double)ones)/s_k.len;
        if (p == 0) {
            e = 0.0;
        } else {
            e = -p*log2(p);
        }
        if (p == 1) {
            g = 0.0;
        } else {
            g = -1*(1-p)*log2(1-p);
        }
        mpf_set_d(l_k, log2(k+2));
        mpf_set_d(t_k, e + g);
#ifdef DEBUG
        gmp_printf("s_k= 0x%Zx\n", s_k.i);
        gmp_printf("t_k= e + g= %Ff\n", t_k);
#endif
        mpf_mul(t_k, t_k, l_k);
#ifdef DEBUG
        gmp_printf("k= %d, t_k= t_k * 2^k= %Ff\n", k, t_k);

        gmp_printf("%Zx %d %d %.2f %.2f %.2f %.2f %.2f %d %d %.2Ff\n",
                s_k.i, ones, s_k.len, p, 1-p, e, g, e + g, k, 1<<k, t_k);
#endif

        mpf_add(l, l, l_k);
        mpf_add(t, t, t_k);
        s_k_new = mpz_bin_d(s_k);
        mpz_set(s_k.i, s_k_new.i);
        s_k.len = s_k_new.len;
        mpz_clear(s_k_new.i);
    }

    mpf_t result;
    mpf_init(result);
    mpf_ui_div(result, 1, l);
    mpf_mul(result, result, t);
    double retval = mpf_get_d(result);
    mpf_clear(result);

    mpf_clear(t);
    mpf_clear(t_k);
    mpf_clear(l);
    mpf_clear(l_k);
    mpz_clear(s_k.i);

    return (retval);
}
