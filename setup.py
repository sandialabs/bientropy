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
from os.path import join
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from distutils.errors import CCompilerError, DistutilsExecError, \
    DistutilsPlatformError

requirements = [
    'bitstring>=3.1.5',
    'numpy>=1.11.2',
    ]

test_requirements = []

if int(platform.python_version_tuple()[0]) < 3:
    requirements.extend(['unittest2', 'mock'])
    test_requirements.extend(['unittest2', 'mock'])

ext_include_dirs = []
ext_library_dirs = []
ext_libs = ['gmp']
package_data = {}

# This is complicated because GMP is not well supported on Windows
if sys.platform == 'win32':
    import shutil
    if 'CONDA_PREFIX' in os.environ:
        CONDA_LIB = join(os.environ['CONDA_PREFIX'], 'Library')
        if not os.path.isfile(join(CONDA_LIB, 'include', 'gmp.h')):
            raise Exception(
                'On Anaconda Python, the MPIR library can be installed using:'
                '\n\n'
                'conda install -c conda-forge mpir')
        # Make sure the DLL gets included in distributions in case a different
        # user does not have the DLL already
        if not os.path.isfile('bientropy/mpir.dll'):
            shutil.copy(join(CONDA_LIB, 'bin', 'mpir.dll'), 'bientropy')
        # Tell setuptools where to find the header and library files
        ext_include_dirs = [join(CONDA_LIB, 'include')]
        ext_library_dirs = [join(CONDA_LIB, 'lib')]
    else:
        # Try to download the library
        import requests, zipfile
        zip_name = 'mpfr_mpir_x86_x64_msvc2010.zip'
        mpir_zip_url = 'http://holoborodko.com/pavel/downloads/'+zip_name
        r = requests.get(mpir_zip_url, stream=True)
        with open(zip_name, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        with zipfile.ZipFile(zip_name, 'r') as z:
            z.extractall('.')
        mpir_dir = zip_name.replace('.zip', '')+'/mpir/dll/x64/Release'
        # Make sure the DLL gets included in distributions in case a different
        # user does not have the DLL already
        if not os.path.isfile('bientropy/mpir.dll'):
            shutil.copy(os.path.join(mpir_dir, 'mpir.dll'), 'bientropy')
        # Tell setuptools where to find the header and library files
        ext_include_dirs = [mpir_dir]
        ext_library_dirs = [mpir_dir]
    # Use MPIR instead of GMP
    ext_libs = ['mpir']
    # Include the DLL in distributions
    package_data['bientropy'] = ['mpir.dll']


MODULE = Extension('bientropy.cbientropy',
                   sources=['ext/bientropy.c',
                            'ext/bientropymodule.c'],
                   include_dirs=ext_include_dirs,
                   library_dirs=ext_library_dirs,
                   libraries=ext_libs,
                  )


if sys.platform == 'win32' and sys.version_info > (2, 6):
   # 2.6's distutils.msvc9compiler can raise an IOError when failing to
   # find the compiler
   # It can also raise ValueError http://bugs.python.org/issue7511
   ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError,
                 IOError, ValueError)
else:
    ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError)


class BuildFailed(Exception):
    pass


class ve_build_ext(build_ext):
    # This class allows C extension building to fail.

    def run(self):
        try:
            build_ext.run(self)
        except (DistutilsPlatformError, BuildFailed):
            raise BuildFailed()

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except ext_errors:
            raise BuildFailed()


def run_setup(with_ext):
    if with_ext:
        kw = dict(
                ext_modules=[MODULE],
                cmdclass=dict(build_ext=ve_build_ext),
                )
    else:
        kw = dict()

    setup(name='BiEntropy',
          version='1.1.0-rc3',
          description='High-performance implementations of BiEntropy metrics '
                      'proposed by Grenville J. Croll',
          url='https://github.com/sandialabs/bientropy',
          author='Ryan Helinski',
          author_email='rhelins@sandia.gov',
          keywords='entropy randomness statistics',
          headers=['ext/bientropy.h'],
          packages=['bientropy', 'bientropy.tests'],
          package_data = package_data,
          install_requires=requirements,
          tests_require=test_requirements,
          test_suite='bientropy.tests',
          classifiers=(
              'Development Status :: 5 - Production/Stable',
              'Topic :: Scientific/Engineering :: Mathematics',
              'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
              'Topic :: Security :: Cryptography'),
          **kw
         )

try:
    run_setup(True)
except BuildFailed:
    print('WARNING: Compiling without C extension')
    run_setup(False)
    print('WARNING: Compiled without C extension')
