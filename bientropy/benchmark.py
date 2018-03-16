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

This file times the C and Python implementations of BiEn and TBiEn and outputs
a table in ASCII format that reports the speedup from the Python implementation
to the C implementation for various lengths of input bitstrings.

To run:
python -m bientropy.benchmark

Example output:

Table of speed-ups:
| Bytes | BiEn    | TBiEn   |
|    16 |     228 |     154 |
|    32 |     214 |     151 |
|    64 |     221 |     158 |
|   128 |     264 |     196 |
|   256 |     337 |     255 |
|   512 |     507 |     374 |
|  1024 |     790 |     533 |

From this, it is clear that the C implementations are hundreds of times faster
than the Python implementation and that the speed-up also improves as the input
bitstring gets longer.

Table of raw times (in ms):
| Bytes | PyBiEn  | PyTBiEn | CBiEn   | CTBiEn  |
|    16 | 6.4e-01 | 5.4e-01 | 2.8e-03 | 3.5e-03 |
|    32 | 1.4e+00 | 1.2e+00 | 6.5e-03 | 8.0e-03 |
|    64 | 3.3e+00 | 2.9e+00 | 1.5e-02 | 1.8e-02 |
|   128 | 8.6e+00 | 7.6e+00 | 3.2e-02 | 3.8e-02 |
|   256 | 2.5e+01 | 2.2e+01 | 7.5e-02 | 8.7e-02 |
|   512 | 8.8e+01 | 7.4e+01 | 1.7e-01 | 2.0e-01 |
|  1024 | 3.6e+02 | 2.7e+02 | 4.5e-01 | 5.0e-01 |

This output is highly machine-dependent, but can be used to compare the
implementations in this package to other implementations.
'''
from __future__ import print_function
import timeit
from . import pybientropy
from . import cbientropy

BYTE_LENGTHS = [16, 32, 64, 128, 256, 512, 1024]
FMAP = {cbientropy.bien: pybientropy.bien,
        cbientropy.tbien: pybientropy.tbien}

def get_n_iters(b_len):
    '''
    This function returns a number of iterations to run one of the BiEntropy
    functions so that the running time is reasonably small.
    '''
    return max(1, int(10*256/b_len))

if __name__ == '__main__':
    RESULTS = {}
    print('Table of speed-ups:')
    print('| Bytes | BiEn    | TBiEn   |')

    for byte_len in BYTE_LENGTHS:
        RESULTS[byte_len] = {}
        print('| %5d'%byte_len, end='')
        for fun in [pybientropy.bien, pybientropy.tbien]:
            timer = timeit.Timer(
                stmt='%s(Bits(bytes=os.urandom(%d)))'%(fun.__name__, byte_len),
                setup='import os; '
                      'from bientropy.pybientropy import bien, tbien; '
                      'from bitstring import Bits')
            n_iters = get_n_iters(byte_len)
            t = timer.timeit(n_iters)
            RESULTS[byte_len][fun] = t/n_iters
        for fun in [cbientropy.bien, cbientropy.tbien]:
            timer = timeit.Timer(
                stmt='%s(os.urandom(%d))'%(fun.__name__, byte_len),
                setup='import os; '
                      'from bientropy.cbientropy import bien, tbien')
            n_iters = get_n_iters(byte_len)
            t = timer.timeit(n_iters)
            RESULTS[byte_len][fun] = t/n_iters
            print(' | %7d'%(RESULTS[byte_len][FMAP[fun]]/(t/n_iters)), end='')
        print(' |')

    print('\nTable of raw times (in ms):')
    print('| Bytes | PyBiEn  | PyTBiEn | CBiEn   | CTBiEn  |')

    for byte_len in BYTE_LENGTHS:
        print('| %5d'%byte_len, end='')
        for fun in [pybientropy.bien, pybientropy.tbien,
                    cbientropy.bien, cbientropy.tbien]:
            print(' | %1.1e'%(RESULTS[byte_len][fun]/t), end='')
        print(' |')
