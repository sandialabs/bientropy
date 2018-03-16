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

This file serves as a demonstration of the BiEntropy and TresBiEntropy
functions and follows some of the computations shown in the paper.
'''
from __future__ import print_function

__author__ = 'Ryan Helinski, Sandia National Laboratories'

from bitstring import Bits

from bientropy.pybientropy import bin_deriv_k
from bientropy import bien, tbien

if __name__ == '__main__':
    # When this file is run as a script, the following tests are executed
    from bientropy.testvectors import BIENTROPY_2BITS, BIENTROPY_4BITS, \
        ORDERING_4BIT, BIENTROPY_8BITS, TBIENTROPY_8BITS

    assert bin_deriv_k(Bits('0b01010101'), 1) == Bits('0b1111111')
    assert bin_deriv_k(Bits('0b00010001'), 3) == Bits('0b11111')
    assert bin_deriv_k(Bits('0b00011111'), 6) == Bits('0b01')

    assert abs(bien(Bits('0b1011')) - 0.95) < 0.01

    assert abs(tbien(Bits('0b1001')) - 0.54) < 0.01

    for s, v in BIENTROPY_2BITS:
        assert abs(bien(s) - v) < 0.01

    for s, v in BIENTROPY_4BITS:
        assert abs(bien(s) - v) < 0.01

    for y in ORDERING_4BIT:
        print(' '.join([
            '%.2f' % bien(Bits(uint=(x<<4) + y, length=8))
            for x in ORDERING_4BIT]))

    for x in ORDERING_4BIT:
        for i, y in enumerate(ORDERING_4BIT):
            a = (x<<4) + y
            ber = bien(Bits(uint=a, length=8))
            tber = tbien(Bits(uint=a, length=8))
            check_key = '%s%s' % (Bits(uint=x, length=4).bin,
                                  Bits(uint=y, length=4).bin)
            assert BIENTROPY_8BITS[check_key] == round(ber, 2)
            assert TBIENTROPY_8BITS[check_key] == round(tber, 2)

            if False:
                # Generate the BIENTROPY_8BITS table used above
                print('\'%s%s\': %.2f,' % (
                    Bits(uint=x, length=4).bin,
                    Bits(uint=y, length=4).bin,
                    ber), end='\n' if i%4 == 3 else '')

                # Generate the TBIENTROPY_8BITS table used above
                print('\'%s%s\': %.2f,' % (
                    Bits(uint=x, length=4).bin,
                    Bits(uint=y, length=4).bin,
                    tber), end='\n' if i%4 == 3 else '')
