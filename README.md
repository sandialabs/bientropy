BiEntropy Randomness Metrics for Python
=======================================

This Python package provides high-performance implementations of the functions
and examples presented in "BiEntropy - The Approximate Entropy of a Finite
Binary String" by Grenville J.  Croll, presented at ANPA 34 in 2013.
https://arxiv.org/abs/1305.0954

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


Performance
-----------

The metrics are implemented in Python using the 'bitstring' package for
handling arbitrary length binary strings and in native C using the GNU Multiple
Precision (GMP) arithmetic library.

The following is a table of speed-ups from the Python to the C implementation
for various string byte lengths:

| Bytes | BiEn    | TBiEn   |
|-------|---------|---------|
|    16 |     229 |     155 |
|    32 |     217 |     149 |
|    48 |     212 |     150 |
|    64 |     221 |     161 |
|   128 |     267 |     196 |
|   256 |     340 |     257 |
|   512 |     502 |     370 |
|  1024 |     802 |     537 |

Following is a log-log plot of the average time to compute the various
implementations of BiEntropy on a 2.40GHz Intel(R) Xeon(R) E5645 CPU versus the
length of the input in bytes.

![Run Times](artwork/bientropy_times.png)


Requirements
------------

This package is tested with Python versions 2.7 and 3.6.

Installation:
* Python http://python.org/
* GCC http://gcc.gnu.org/
* libgmp http://gmplib.org/
* bitstring http://pythonhosted.org/bitstring/
* NumPy http://numpy.org/

For running tests:
* pytest http://pytest.org/


Installation
------------

You will need to install the GMP library if not installing from a wheel.

On Debian/Ubuntu:
```
apt-get install libgmp-dev
```

On RedHat:
```
yum install gmp-devel
```

Then, use `setup.py` to compile and install the package:
```
python setup.py install
```

Optionally, you can run the unit tests with the following command:
```
python setup.py test
```

You can test your installation with this command:
```
python -m bientropy.demo
```

This file (`bientropy/demo.py`) also serves as a good starting point for using
the code.


Development
-----------

To compile with debug symbols and with extra output, use:
```
python setup.py build_ext --force --debug --define DEBUG
```

To also disable compiler optimizations, use:
```
CFLAGS=-O0 python setup.py build_ext --force --debug --define DEBUG
```

To debug the extension with GDB:
```
$ gdb python
(gdb) run setup.py test
```

To run the Valgrind memcheck tool to check for memory corruption and leaks:
```
valgrind --xml=yes --xml-file=valgrind.xml ${python} setup.py test
```


Authors
-------

This package, consisting of the C implementations, Python implementations and
Python bindings were written by Ryan Helinski <rhelins@sandia.gov>.


License
-------
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
