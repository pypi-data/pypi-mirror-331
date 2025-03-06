from setuptools import setup, find_packages
setup(
    name='zwoeafpy',
    version='0.4.0',
    author='William Fox',
    author_email='foxwilliamcarr@gmail.com',
    description='Python binding for the ZWO Electronic Automatic Focuser (EAF) SDK',
    long_description='Python binding for the ZWO Electronic Automatic Focuser (EAF) SDK',
    url='https://github.com/Willcarr99/zwoeafpy',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    license_files=('LICENSE'),
    python_requires='>=3.2' # Found from the vermin PyPI package ('vermin path/to/my_package')
)