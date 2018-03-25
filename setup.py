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

On the Windows platform, the MPIR library http://mpir.org/ is used.
'''
import platform
import sys
import os
from setuptools import setup, Extension

requirements = [
    'bitstring>=3.1.5',
    'numpy>=1.11.2',
    ]

test_requirements = []

if int(platform.python_version_tuple()[0]) < 3:
    requirements.append('mock')
    test_requirements.append('mock')

ext_include_dirs = []
ext_library_dirs = []
ext_libs = ['gmp']
package_data = {}

if sys.platform == 'win32':
    mpir_dir = 'mpir/dll/x64/Release'
    if not os.path.isdir(mpir_dir):
        raise Exception('''This package can be compiled with MPIR on Windows.
The source for MPIR is available at http://mpir.org/
The header files, library files and DLL are expected under %s

A compiled distribution of MPIR was also available at:
http://www.holoborodko.com/pavel/mpfr/#download
Download 'MPFR-MPIR-x86-x64-MSVC2010.zip'.
Extract 'mpir' from the ZIP file to this directory.
''' % mpir_dir)
    import shutil
    if not os.path.isfile('bientropy/mpir.dll'):
        shutil.copy(os.path.join(mpir_dir, 'mpir.dll'), 'bientropy')
    ext_include_dirs = [mpir_dir]
    ext_library_dirs = [mpir_dir]
    ext_libs = ['mpir']
    package_data['bientropy'] = ['mpir.dll']

MODULE = Extension('bientropy.cbientropy',
                   sources=['ext/bientropy.c',
                            'ext/bientropymodule.c'],
                   include_dirs=ext_include_dirs,
                   library_dirs=ext_library_dirs,
                   libraries=ext_libs,
                  )

setup(name='BiEntropy',
      version='1.0.4',
      description='High-performance implementations of BiEntropy metrics '
                  'proposed by Grenville J. Croll',
      ext_modules=[MODULE],
      url='https://github.com/sandialabs/bientropy',
      author='Ryan Helinski',
      author_email='rhelins@sandia.gov',
      keywords='entropy randomness statistics',
      headers=['ext/bientropy.h'],
      packages=['bientropy'],
      package_data = package_data,
      install_requires=requirements,
      tests_require=test_requirements,
      test_suite='bientropy.test_suite'
     )
