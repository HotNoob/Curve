# setup.py
from setuptools import find_packages, setup
from setuptools.extension import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext

setup(
    name="classes.Plot",
    version='0.100', 
    ext_modules = cythonize(
        [
            Extension(name="*",sources=[ "./Plot/*.py"]),
        ],
        compiler_directives={
            'language_level' : "3",
            'always_allow_keywords': True,
        },
        build_dir="../build/"
    ),
   # packages=['classes.Plot']
)