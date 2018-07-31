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

This Python package, written by Ryan Helinski, provides high-performance
implementations of the functions and examples presented in "BiEntropy -
The Approximate Entropy of a Finite Binary String" by Grenville J.  Croll,
presented at ANPA 34 in 2013. https://arxiv.org/abs/1305.0954

According to the paper, BiEntropy is "a simple algorithm which computes the
approximate entropy of a finite binary string of arbitrary length" using "a
weighted average of the Shannon Entropies of the string and all but the last
binary derivative of the string." In other words, these metrics can be used to
help assess the disorder or randomness of binary or byte strings, particularly
those that are too short for other randomness tests.

This module includes both a Python C extension and a pure Python module
implementing the BiEn and TBiEn metrics from the paper, as well as a suite of
tests that verify their correctness. These implementations are available under
the submodules 'cbientropy' and 'pybientropy'.

Aliases of C versions of BiEn and TBiEn are included at the top level of this
module for convenience.
'''

from . import pybientropy
try:
    from .cbientropy import bien, tbien
except ImportError:
    import warnings
    warnings.warn('Unable to import C extension. Using slower Python '
        'implementations instead', Warning)
    from .pybientropy import bien, tbien
