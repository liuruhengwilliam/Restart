from distutils.core import setup
import py2exe
import glob

data_files = [(r'mpl-data', glob.glob(r'C:\ProgramData\Anaconda2\Lib\site-packages\matplotlib\mpl-data\*.*')),
    (r'mpl-data', [r'C:\ProgramData\Anaconda2\Lib\site-packages\matplotlib\mpl-data\matplotlibrc']),
    (r'mpl-data\stylelib',glob.glob(r'C:\ProgramData\Anaconda2\Lib\site-packages\matplotlib\mpl-data\stylelib\*.*')),
    (r'mpl-data\images',glob.glob(r'C:\ProgramData\Anaconda2\Lib\site-packages\matplotlib\mpl-data\images\*.*')),
    (r'mpl-data\fonts',glob.glob(r'C:\ProgramData\Anaconda2\Lib\site-packages\matplotlib\mpl-data\fonts\*.*'))]

setup(
    version='2.1.5',
    description='Project RESTART. Marked by liuruheng on 2017-11-13',
    name = 'alpha V2.1.5',
    windows=[r'AssistantGUI.py'],data_files=data_files)