from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize

setup(
    version='2.4.0',
    description='Optimizated by liuruheng from 2018-07-09',
    name = 'V2.4.0',
    ext_modules = cythonize(Extension(
    'DataScrape',
    sources=['DataScrape.pyx']
    ))
)
