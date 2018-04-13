"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='sitchensis',  
    version='1.0.0',  
    description='Error checking and visualization for tree mapping data',  
    long_description=long_description, 
    long_description_content_type='text/markdown', 
    url='https://github.com/northcoastmountainrat/Sitchensis', 
    author='Russell Kramer',  # Optional
    author_email='russelld.kramer@gmail.com',  
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: CanopyScientists',
        'Topic :: TreeMapping :: Visualization and error screening',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.x',
        ],
    keywords='error checking, data visualization, 3D', 
    packages=find_packages(exclude=['contrib', 'docs', 'SitchenisTests', 'Templates']), 
    install_requires=[
		'xlrd>=1.1.0',
		'pandas>=0.22.0',
		'vpython>=7.4.3',
		'numpy>=1.13.3',
		'matplotlib>=2.1.0',
	        'scipy>=0.19.1',
		'xlsxwriter>=1.0.2',
	        #'numbers',  # I think all these are native to python so not needed
		#'tkinter',
		#'os',
		#'sys',
		],

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    # #extras_require={  # Optional
    # #    'dev': ['check-manifest'],
    # #    'test': ['coverage'],
    # #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.
	#I should install some test files I suppose
    # # package_data={  # Optional
        # # 'sample': ['package_data.dat'],
    # # },

    #Technically I should have a scripts arguement here and just name the script something useable	
    entry_points={
        'console_scripts': [
            'run_tree = sitchensis.MainBodyScript.py',
        ],
     },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/northcoastmountainrat/sitchensis/issues',
        # 'Funding': 'https://donate.pypi.org',
        # 'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://github.com/northcoastmountainrat/sitchensis',
     },
)
