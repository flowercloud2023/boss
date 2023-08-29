from distutils.core import setup
from Cython.Build import cythonize

# python setup_package.py build_ext --inplace
setup(
    name='bee',
    ext_modules=cythonize("aunit.py"),
)