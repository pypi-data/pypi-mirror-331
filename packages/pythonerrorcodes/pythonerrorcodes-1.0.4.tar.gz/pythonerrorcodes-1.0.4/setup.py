from setuptools import setup, find_packages

VERSION = '1.0.4' 
DESCRIPTION = 'Error Code for Python Module'


# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="pythonerrorcodes", 
        version='1.0.4',
        author="Snigdha Dutta",
        author_email="",
        description="DESCRIPTION",
        long_description="LONG_DESCRIPTION",
        packages=find_packages(),
        install_requires=[], 
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)