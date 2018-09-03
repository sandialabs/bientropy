'''
NOTICE

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

This file tests the Python and C implementations of BiEntropy in this package.
It checks them against many values reported in the paper and it checks the
Python and C implementations against eachother.
'''
from __future__ import print_function
import os
import sys
from multiprocessing import Pool, cpu_count
from itertools import repeat
import warnings

try:
    from unittest.mock import patch, call, MagicMock
    from unittest import TestCase, main, skipIf
    PY3 = True
except ImportError:
    from mock import patch, call, MagicMock
    from unittest2 import TestCase, main, skipIf
    PY3 = False

from bitstring import Bits
try:
    from bientropy import cbientropy
    NO_CEXT = ''
except ImportError as e:
    # Allow some tests to be skipped
    NO_CEXT = 'C extension not available'

from bientropy import pybientropy
from bientropy.pybientropy import bin_deriv_k, p_k

from bientropy.testvectors import BIENTROPY_2BITS, BIENTROPY_4BITS, \
    ORDERING_4BIT, BIENTROPY_8BITS, TBIENTROPY_8BITS, PRIMES


def round_fun(x):
    '''Common numeric round function'''
    return round(x, 2)


def run_large_byte_strings(s_byte_len=128, tolerance=0.001):
    ti = os.urandom(s_byte_len)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        pybien = pybientropy.bien(Bits(bytes=ti))
        cbien = cbientropy.bien(ti)
    assert abs(pybien - cbien) < tolerance
    pytbien = pybientropy.tbien(Bits(bytes=ti))
    ctbien = cbientropy.tbien(ti)
    assert abs(pytbien - ctbien) < tolerance

    return ti, cbien, ctbien



class BiEntropyTests(TestCase):
    'Test the C and Python implementaions'

    def check_ordering_4bit(self, fun, sols):
        '''Check that the 4-bit ordering sequence is the same
        as the one found in the paper for a particular function'''
        for x in ORDERING_4BIT:
            for y in ORDERING_4BIT:
                a = (x<<4) + y
                b = Bits(uint=a, length=8)
                r = fun(b)

                check_key = '%s%s' % (
                    Bits(uint=x, length=4).bin,
                    Bits(uint=y, length=4).bin)
                with self.subTest(check_key=check_key):
                    self.assertEqual(sols[check_key], round_fun(r))


    def test_bin_deriv_k(self):
        'Check the k^th binary derivate examples from the paper'
        self.assertEqual(bin_deriv_k(Bits('0b01010101'), 1), Bits('0b1111111'))
        self.assertEqual(bin_deriv_k(Bits('0b00010001'), 3), Bits('0b11111'))
        self.assertEqual(bin_deriv_k(Bits('0b00011111'), 6), Bits('0b01'))


    def test_p_k(self):
        'Check the p_k(x) examples from the paper'
        self.assertEqual(p_k(Bits('0b01010101'), 1), 1.0)
        self.assertEqual(p_k(Bits('0b00010001'), 3), 1.0)
        self.assertEqual(p_k(Bits('0b00011111'), 6), 0.5)


    @skipIf(NO_CEXT, NO_CEXT)
    def test_cbientropy_2bit(self):
        'Check the C BiEn function against the 2-bit strings'
        for b, r in BIENTROPY_2BITS:
            with self.subTest(b=b, r=r):
                self.assertEqual(round_fun(cbientropy.bien(b)), r)


    @skipIf(NO_CEXT, NO_CEXT)
    def test_cbientropy_4bit(self):
        'Check the C BiEn function against the 4-bit strings'
        for b, r in BIENTROPY_4BITS:
            with self.subTest(b=b, r=r):
                self.assertEqual(round_fun(cbientropy.bien(b)), r)


    def test_pybientropy_2bit(self):
        'Check the Python BiEn implementation with 2-bit strings'
        for b, r in BIENTROPY_2BITS:
            with self.subTest(b=b, r=r):
                self.assertEqual(round_fun(pybientropy.bien(b)), r)


    def test_pybientropy_4bit(self):
        'Check the Python BiEn implementation with 4-bit strings'
        for b, r in BIENTROPY_4BITS:
            with self.subTest(b=b, r=r):
                self.assertEqual(round_fun(pybientropy.bien(b)), r)


    @skipIf(NO_CEXT, NO_CEXT)
    def test_cbientropy(self):
        'Check the C BiEn implementation with 8-bit strings'
        self.check_ordering_4bit(cbientropy.bien, BIENTROPY_8BITS)


    def test_pybientropy(self):
        'Check the Python BiEn implementation with 8-bit strings'
        self.check_ordering_4bit(pybientropy.bien, BIENTROPY_8BITS)


    @skipIf(NO_CEXT, NO_CEXT)
    def test_ctbientropy(self):
        'Check the C TBiEn implementation with 8-bit strings'
        self.check_ordering_4bit(cbientropy.tbien, TBIENTROPY_8BITS)


    def test_pytbientropy(self):
        'Check the Python TBiEn implementation with 8-bit strings'
        self.check_ordering_4bit(pybientropy.tbien, TBIENTROPY_8BITS)


    @skipIf(NO_CEXT, NO_CEXT)
    def test_c_bytes_vs_obj(self, max_s_len=128):
        '''
        Check that the C Bien and TBiEn compute the same result for both string
        and bitstring input types
        '''
        for s_len in range(1, max_s_len):
            with self.subTest(s_len=s_len):
                ti = os.urandom(s_len)
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    self.assertEqual(cbientropy.bien(Bits(bytes=ti)),
                                     cbientropy.bien(ti))
                self.assertEqual(cbientropy.tbien(Bits(bytes=ti)),
                                 cbientropy.tbien(ti))


    def test_py_bytes_vs_obj(self, max_s_len=24):
        '''
        Check that the Python implementation of BiEn handles binary string
        input correctly.
        '''
        for s_len in range(1, max_s_len):
            with self.subTest(s_len=s_len):
                ti = os.urandom(s_len)
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    self.assertEqual(pybientropy.bien(Bits(bytes=ti)),
                                     pybientropy.bien(ti))
                self.assertEqual(pybientropy.tbien(Bits(bytes=ti)),
                                 pybientropy.tbien(ti))


    @skipIf(NO_CEXT, NO_CEXT)
    def test_odd_sizes(self):
        '''
        Check that the Python and C implementations for BiEn and TBiEn match
        for bit strings with prime-number lengths.
        '''
        input_set = set()
        for prime in PRIMES:
            with self.subTest(prime=prime):
                rand_s = Bits(bytes=os.urandom(int(prime/8+1)))[:prime]
                input_set = input_set.union([rand_s])
                self.assertEqual(len(rand_s), prime)
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    self.assertAlmostEqual(cbientropy.bien(rand_s),
                                           pybientropy.bien(rand_s))
                self.assertAlmostEqual(cbientropy.tbien(rand_s),
                                       pybientropy.tbien(rand_s))

        # check that all the strings are distinct
        self.assertEqual(len(input_set), len(PRIMES))


    @skipIf(NO_CEXT, NO_CEXT)
    def test_large_strings(self, num_s=2**4, s_byte_len=256):
        '''
        Check that the Python and C implementations for BiEn and TBiEn match
        for longer bit strings.
        '''
        if not PY3 or sys.platform == 'win32':
            map_fun = map
        else:
            pool = Pool(cpu_count())
            map_fun = pool.map

        results = map_fun(run_large_byte_strings, repeat(s_byte_len, num_s))
        if map_fun != map:
            pool.close()
        # check that all the strings are distinct
        self.assertEqual(
            len(set([result[0] for result in results])),
            num_s)


    @patch('bientropy.pybientropy.DEBUG', new=True)
    def test_pytbien_debug(self):
        'Check that Python TBiEn has the correct progression of state'
        with patch('builtins.print' \
                   if PY3 else '__builtin__.print') as mock_print:
            pybientropy.tbien(Bits('0b1011'))
        mock_print.assert_has_calls([
            call('      1011 3 4 0.75 0.25 0.31 0.50 0.81 0 1.00 0.81'),
            call('       110 2 3 0.67 0.33 0.39 0.53 0.92 1 1.58 1.46'),
            call('        01 1 2 0.50 0.50 0.50 0.50 1.00 2 2.00 2.00'),
            call('4.585'),
            call('4.267')
            ])


    @patch('bientropy.pybientropy.DEBUG', new=True)
    def test_pybien_debug(self):
        'Check that Python BiEn has the correct progression of state'
        with patch('builtins.print' \
                   if PY3 else '__builtin__.print') as mock_print:
            pybientropy.bien(Bits('0b1011'))
        mock_print.assert_has_calls([
            call('      1011 3 4 0.75 0.25 0.31 0.50 0.81 0 1 0.81'),
            call('       110 2 3 0.67 0.33 0.39 0.53 0.92 1 2 1.84'),
            call('        01 1 2 0.50 0.50 0.50 0.50 1.00 2 4 4.00'),
            call('6.648')
            ])


    @skipIf(NO_CEXT, NO_CEXT)
    def test_error_bad_tobytes(self):
        '''
        Check that C BiEn and TBiEn behave correctly when the tobytes() method
        of the input object raises an exception
        '''
        m_obj = MagicMock()
        m_obj.tobytes.side_effect = Exception('bad')
        for fun in [cbientropy.bien, cbientropy.tbien]:
            with self.subTest(fun=fun):
                m_obj.reset_mock()
                with self.assertRaises(Exception):
                    fun(m_obj)
                m_obj.tobytes.assert_called_once_with()


    @skipIf(NO_CEXT, NO_CEXT)
    def test_error_bad_tobytes_retval(self):
        '''
        Check that C BiEn and TBiEn behave correctly when the tobytes() method
        of the input object returns something other than a byte string
        '''
        m_obj = MagicMock()
        m_obj.tobytes.return_value = 42
        for fun in [cbientropy.bien, cbientropy.tbien]:
            with self.subTest(fun=fun):
                m_obj.reset_mock()
                with self.assertRaises(ValueError):
                    fun(m_obj)
                m_obj.tobytes.assert_called_once_with()


    @skipIf(NO_CEXT, NO_CEXT)
    def test_error_bad_len(self):
        '''
        Check that C BiEn and TBiEn enforce that value of the len() method of
        the input object is in bits and not bytes
        '''
        m_obj = MagicMock()
        m_obj.tobytes.return_value = b'\xde\xad\xbe\xef'
        for m_obj.__len__.return_value in [4, 23, 33]:
            for fun in [cbientropy.bien, cbientropy.tbien]:
                with self.subTest(len=m_obj.__len__.return_value, fun=fun):
                    m_obj.reset_mock()
                    with self.assertRaises(TypeError):
                        fun(m_obj)
                    m_obj.__len__.assert_called_with()


    @skipIf(NO_CEXT, NO_CEXT)
    def test_error_bad_obj(self):
        '''
        Check that C BiEn and TBiEn raise an exception if the input object is
        not a byte string and does not have a len() method
        '''
        m_obj = 1984 # not a string and does not have a tobytes() method
        for fun in [cbientropy.bien, cbientropy.tbien]:
            with self.subTest(fun=fun):
                with self.assertRaises(TypeError):
                    fun(m_obj)


    @skipIf(NO_CEXT, NO_CEXT)
    def test_error_empty(self):
        '''
        Check that C BiEn and TBiEn raise an exception if the input object has
        a zero length
        '''
        for empty in [b'', Bits()]:
            for fun in [cbientropy.bien, cbientropy.tbien]:
                with self.subTest(empty=empty, fun=fun):
                    with self.assertRaises(ValueError):
                        fun(empty)


    def test_error_tbien_short(self):
        '''
        Check that C TBiEn raises an exception if the input object has
        too short of a length
        '''
        for short in [Bits(uint=0, length=1), Bits(uint=1, length=1)]:
            funs = [pybientropy.tbien]
            if not NO_CEXT:
                funs.append(cbientropy.tbien)
            for fun in funs:
                with self.subTest(short=short, fun=fun):
                    with self.assertRaises(ValueError):
                        fun(short)


    @skipIf(sys.version_info.major<3 or sys.version_info.minor<4,
            'Bug with Python warning filters. See '
            'https://bugs.python.org/msg75117')
    def test_warn_bien_long(self):
        '''
        Check that C BiEn issues a warning if the input object has
        too long of a length
        '''
        for inp, outp in [(Bits(uint=42, length=33), 0.450868398),
                          (Bits(uint=57, length=64), 0.236565114)]:
            funs = [pybientropy.bien]
            if not NO_CEXT:
                funs.append(cbientropy.bien)
            for fun in funs:
                with self.subTest(inp=inp, fun=fun):
                    with warnings.catch_warnings(record=True) as w:
                        warnings.simplefilter('always')
                        retval = fun(inp)
                        self.assertEqual(len(w), 1)
                        self.assertTrue(issubclass(w[-1].category, Warning))
                        self.assertAlmostEqual(retval, outp)


if __name__ == '__main__':
    main()
