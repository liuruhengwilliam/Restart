from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize

setup(
    version='2.4.0',
    description='Optimizated by liuruheng from 2018-07-10',
    name = 'V2.4.0',
    ext_modules = cythonize(Extension(
    'StrategyCheck',
    sources=['StrategyCheck.pyx']
    ))
)
