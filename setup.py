__version__ = "0.0.1"
import os
from setuptools import setup, find_packages

def _read_contents(fn):
	here = os.path.dirname( os.path.realpath(__file__) )
	filename = os.path.join(here, fn)
	with open(filename) as file:
		return file.read()

setup(
	name='useless.pipes',
	version=__version__,
	description='Sugar around generators.',
	long_description=_read_contents('README'),
	author="herr kaste",
	author_email="herr.kaste@gmail.com",
	url='http://github.com/kaste/useless.pipes',
	packages=find_packages(exclude=['tests']),
	install_requires=[],
	tests_require=[],
	classifiers= [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        ],
)