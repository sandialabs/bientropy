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

BiEntropy for Python - setup.py
This file allows the user to compile, test and install the package using
the `setuptools` package. See the README for more information.
'''
import platform
from setuptools import setup, Extension

MODULE = Extension('bientropy.cbientropy',
                   sources=['ext/bientropy.c',
                            'ext/bientropymodule.c'],
                   include_dirs=[],
                   libraries=['gmp'],
                  )

requirements = [
    'bitstring>=3.1.5',
    'numpy>=1.11.2',
    ]

test_requirements = [
    'pytest'
    ]

if int(platform.python_version_tuple()[0]) < 3:
    test_requirements.append('mock')

setup(name='BiEntropy',
      version='1.0',
      description='High-performance implementations of BiEntropy metrics '
                  'proposed by Grenville J. Croll',
      ext_modules=[MODULE],
      url='https://github.com/sandialabs/bientropy',
      author='Ryan Helinski',
      author_email='rhelins@sandia.gov',
      license='GPLv3',
      keywords='entropy randomness statistics',
      headers=['ext/bientropy.h'],
      packages=['bientropy'],
      install_requires=requirements,
      setup_requires=['pytest-runner'],
      tests_require=test_requirements,
      test_suite='bientropy.test_suite'
     )
