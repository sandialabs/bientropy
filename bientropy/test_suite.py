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
from multiprocessing import Pool, cpu_count

from pytest import approx, raises

try:
    from unittest.mock import patch, call, MagicMock
    PY3 = True
except ImportError:
    from mock import patch, call, MagicMock
    PY3 = False

from bitstring import Bits
from . import cbientropy
from . import pybientropy
from .pybientropy import bin_deriv_k, p_k

from .testvectors import BIENTROPY_2BITS, BIENTROPY_4BITS, ORDERING_4BIT, \
    BIENTROPY_8BITS, TBIENTROPY_8BITS, PRIMES

def round_fun(x):
    """Common numeric round function"""
    return round(x, 2)

def test_bin_deriv_k():
    assert bin_deriv_k(Bits('0b01010101'), 1) == Bits('0b1111111')
    assert bin_deriv_k(Bits('0b00010001'), 3) == Bits('0b11111')
    assert bin_deriv_k(Bits('0b00011111'), 6) == Bits('0b01')

def test_p_k():
    assert p_k(Bits('0b01010101'), 1) == 1.0
    assert p_k(Bits('0b00010001'), 3) == 1.0
    assert p_k(Bits('0b00011111'), 6) == 0.5

def check_ordering_4bit(fun, sols):
    """Check that the 4-bit ordering sequence is the same
    as the one found in the paper"""
    for x in ORDERING_4BIT:
        for y in ORDERING_4BIT:
            a = (x<<4) + y
            b = Bits(uint=a, length=8)
            r = fun(b)

            check_key = '%s%s' % (
                Bits(uint=x, length=4).bin,
                Bits(uint=y, length=4).bin)
            assert sols[check_key] == round_fun(r)
            print('%s(%s): %.2f' % (fun.__name__, b.bin, r))

def test_cbientropy_2bit():
    for b, r in BIENTROPY_2BITS:
        assert round_fun(cbientropy.bien(b)) == r

def test_cbientropy_4bit():
    for b, r in BIENTROPY_4BITS:
        assert round_fun(cbientropy.bien(b)) == r

def test_pybientropy_2bit():
    "Check the Python BiEn implementation with 2-bit strings"
    for b, r in BIENTROPY_2BITS:
        assert round_fun(pybientropy.bien(b)) == r

def test_pybientropy_4bit():
    "Check the Python BiEn implementation with 4-bit strings"
    for b, r in BIENTROPY_4BITS:
        assert round_fun(pybientropy.bien(b)) == r

def test_cbientropy():
    "Check the C BiEn implementation with 8-bit strings"
    check_ordering_4bit(cbientropy.bien, BIENTROPY_8BITS)

def test_pybientropy():
    "Check the Python BiEn implementation with 8-bit strings"
    check_ordering_4bit(pybientropy.bien, BIENTROPY_8BITS)

def test_ctbientropy():
    "Check the C TBiEn implementation with 8-bit strings"
    check_ordering_4bit(cbientropy.tbien, TBIENTROPY_8BITS)

def test_pytbientropy():
    "Check the Python TBiEn implementation with 8-bit strings"
    check_ordering_4bit(pybientropy.tbien, TBIENTROPY_8BITS)

def test_c_bytes_vs_obj(max_s_len=128):
    for s_len in range(1, max_s_len):
        ti = os.urandom(s_len)
        assert cbientropy.bien(Bits(bytes=ti)) == cbientropy.bien(ti)
        assert cbientropy.tbien(Bits(bytes=ti)) == cbientropy.tbien(ti)

def test_odd_sizes():
    for prime in PRIMES:
        rand_s = Bits(bytes=os.urandom(int(prime/8+1)))[:prime]
        assert len(rand_s) == prime
        assert cbientropy.bien(rand_s) == approx(pybientropy.bien(rand_s))
        assert cbientropy.tbien(rand_s) == approx(pybientropy.tbien(rand_s))


def run_large_strings(index, s_len=128, tolerance=0.001):
    ti = os.urandom(s_len)
    pybien = pybientropy.bien(Bits(bytes=ti))
    cbien = cbientropy.bien(ti)
    assert abs(pybien - cbien) < tolerance
    pytbien = pybientropy.tbien(Bits(bytes=ti))
    ctbien = cbientropy.tbien(ti)
    assert abs(pytbien - ctbien) < tolerance

def test_large_strings(num_s=2**6, s_len=256, tolerance=0.001):
    """
    Ensure that the Python and C implementations for BiEn and TBiEn match for
    longer bit strings.
    """
    p = Pool(cpu_count())
    p.map(run_large_strings, range(num_s))
    p.close()

@patch('bientropy.pybientropy.DEBUG', new=True)
def test_pytbien_debug():
    with patch('builtins.print' if PY3 else '__builtin__.print') as mock_print:
        pybientropy.tbien(Bits('0b1011'))
    mock_print.assert_has_calls([
        call('      1011 3 4 0.75 0.25 0.31 0.50 0.81 0 1.00 0.81'),
        call('       110 2 3 0.67 0.33 0.39 0.53 0.92 1 1.58 1.46'),
        call('        01 1 2 0.50 0.50 0.50 0.50 1.00 2 2.00 2.00'),
        call('4.585'),
        call('4.267')
        ])

@patch('bientropy.pybientropy.DEBUG', new=True)
def test_pybien_debug():
    with patch('builtins.print' if PY3 else '__builtin__.print') as mock_print:
        pybientropy.bien(Bits('0b1011'))
    mock_print.assert_has_calls([
        call('      1011 3 4 0.75 0.25 0.31 0.50 0.81 0 1 0.81'),
        call('       110 2 3 0.67 0.33 0.39 0.53 0.92 1 2 1.84'),
        call('        01 1 2 0.50 0.50 0.50 0.50 1.00 2 4 4.00'),
        call('6.648')
        ])

def test_error_bad_tobytes():
    m_obj = MagicMock()
    m_obj.tobytes.side_effect = Exception('bad')
    for fun in [cbientropy.bien, cbientropy.bien]:
        m_obj.reset_mock()
        with raises(Exception) as e:
            fun(m_obj)
        m_obj.tobytes.assert_called_once()


def test_error_bad_tobytes_retval():
    m_obj = MagicMock()
    m_obj.tobytes.return_value = 42
    for fun in [cbientropy.bien, cbientropy.tbien]:
        m_obj.reset_mock()
        with raises(ValueError) as e:
            fun(m_obj)
        m_obj.tobytes.assert_called_once()


def test_error_bad_len():
    '''
    The value of len() should be in bits and not bytes
    '''
    m_obj = MagicMock()
    m_obj.tobytes.return_value = b'\xde\xad\xbe\xef'
    for m_obj.__len__.return_value in [4, 23, 33]:
        for fun in [cbientropy.bien, cbientropy.tbien]:
            m_obj.reset_mock()
            with raises(TypeError) as e:
                fun(m_obj)
            m_obj.__len__.assert_called()


def test_error_bad_obj():
    m_obj = 1984 # not a string and does not have a tobytes() method
    for fun in [cbientropy.bien, cbientropy.tbien]:
        with raises(TypeError) as e:
            fun(m_obj)


def test_error_empty():
    for empty in [b'', Bits()]:
        for fun in [cbientropy.bien, cbientropy.tbien]:
            with raises(ValueError) as e:
                fun(empty)


if __name__ == '__main__':
    print("""Trying running with:
    $ pytest
or:
    $ python -m pytest
""")
