from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize

setup(
    version='2.4.3',
    description='Optimizated by liuruheng from 2018-07-19',
    name = 'V2.4.3',
    ext_modules = cythonize(Extension(
    'Coordinate',
    sources=['Coordinate.pyx']
    ))
)
