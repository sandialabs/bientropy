'''
Copyright 2018 National Technology & Engineering Solutions of Sandia, LLC
(NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
Government retains certain rights in this software.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

This module implements the metrics defined in the paper with pure Python code.
'''
from __future__ import print_function

__author__ = 'Ryan Helinski, Sandia National Laboratories'
__version__ = '1.0'

from math import log
from decimal import Decimal

DEBUG = False

def bin_deriv(bits):
    """
    The binary derivative is computed using the exclusive or (XOR) of all
    adjacent bit positions in a bitstring.

    Parameters
    ----------
    bits : bitstring-like object
        the input bitstring with length n

    Returns
    -------
    bitstring-like object
        the binary derivative of the input bitstring with length n-1
    """
    return bits[1:] ^ bits[:-1]

def bin_deriv_k(bits, k):
    """
    Return the kth binary derivative of the string 'bits'

    Parameters
    ----------
    bits : bitstring-like object
        the input bitstring with length n
    k : integer
        the number of repeated binary derivatives

    Returns
    -------
    bitstring-like object
        the kth binary derivative of length n-k where n is the length of the input
    """
    return bits if k == 0 else bin_deriv(bin_deriv_k(bits, k-1))

def p_k(bits, k):
    """
    p(k) denotes the observed fraction of 1's in bin_deriv_k(bits)
    where p(0) denotes the fraction of 1's in bits.

    Parameters
    ----------
    bits : bitstring-like object
        the input bitstring of length n
    k : integer
        the number of repeated binary derivates

    Returns
    -------
    float
        the fraction of 1's in the kth binary derivative of the input bitstring
    """
    return float(bin_deriv_k(bits, k).count(1)) / (bits.len - k)

def bien(bits):
    """
    BiEntropy, or BiEn for short, is a weighted average of the Shannon binary
    entropies of the string and the first n-2 binary derivatives of the string
    using a simple power law. This version of BiEntropy is suitable for
    shorter binary strings where n <= 32, approximately.

    This algorithm evaluates the order and disorder of a binary string of
    length n in O(n^2) time using O(n) memory.

    Parameters
    ----------
    bits : bitstring-like object
        the input bitstring on which to operate

    Returns
    -------
    float
        the BiEntropy of the input
    """
    t = Decimal(0)
    s_k = bits
    for k in range(bits.len - 1):
        ones = s_k.count(1)
        n = s_k.len
        p = float(ones) / n
        e = 0 if p == 0 else -p*log(p, 2)
        g = 0 if p == 1 else -1*(1-p)*log(1-p, 2)
        t_k = Decimal(e + g) * Decimal(2**k)

        if DEBUG:
            print('%10s %d %d %.2f %.2f %.2f %.2f %.2f %d %d %.2f' % (
                s_k.bin, ones, n, p, 1-p, e, g, e + g, k, 2**k, t_k))
        t += t_k
        s_k = bin_deriv(s_k)
    if DEBUG:
        print('%.3f' % t)
    return float(t/Decimal(2**(bits.len-1) - 1))

def tbien(bits):
    """
    The logarithmic weighting BiEntropy, or TBiEn for short, gives greater
    weight to the higher binary derivatives. As a result, has a slightly faster
    runtime because the weights tend to be smaller than for BiEn.

    This algorithm evaluates the order and disorder of a binary string of
    length n in O(n^2) time using O(n) memory.

    Parameters
    ----------
    bits : bitstring-like object
        the input bitstring on which to operate

    Returns
    -------
    float
        the TBiEntropy of the input
    """
    l = 0
    t = 0
    s_k = bits
    for k in range(bits.len - 1):
        ones = s_k.count(1)
        n = s_k.len
        p = float(ones) / n
        e = 0 if p == 0 else -p*log(p, 2)
        g = 0 if p == 1 else -1*(1-p)*log(1-p, 2)
        l_k = log(k+2, 2)
        t_k = (e + g) * l_k

        if DEBUG:
            print('%10s %d %d %.2f %.2f %.2f %.2f %.2f %d %.2f %.2f' % (
                s_k.bin, ones, n, p, 1-p, e, g, e + g, k, l_k, t_k))
        l += l_k
        t += t_k
        s_k = bin_deriv(s_k)
    if DEBUG:
        print('%.3f' % l)
        print('%.3f' % t)
    return (1. / l)*t
