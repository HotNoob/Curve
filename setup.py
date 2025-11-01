# setup.py
from setuptools import find_packages, setup
from setuptools.extension import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext

import subprocess
import os
import numpy

from setuptools import setup, find_packages

setup(name='Curve', version='1.0', packages=find_packages())



print(__file__)
print('start')

os.chdir('classes/')

subprocess.call("python setup.py build_ext --inplace", shell=True)

quit()
setup(
    ext_modules=cythonize([
        Extension('package.cython_code1', ['package/cython_code1.pyx']),
        Extension('package.cython_code1', ['package/cython_code2.pyx']),
    ]),
    include_dirs=[numpy.get_include()],
)
