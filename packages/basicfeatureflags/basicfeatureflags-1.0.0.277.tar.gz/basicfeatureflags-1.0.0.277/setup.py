from setuptools import setup, find_packages

setup(
    name='basicfeatureflags', # no kebab-casing, or the import won't work 
    version='1.0.0.277',
    author='Albert Willett Jr',
    author_email='albert.willett2@gmail.com',
    description='Basic Implementation of Feature Flags in Python',
    packages=find_packages(),
    install_requires=[
        # List the package names of your project's dependencies here
        'PyYAML==6.0.2',
    ],
    classifiers=[
        'Intended Audience :: Developers',
		'Programming Language :: Python :: 3.12',
    ],
)