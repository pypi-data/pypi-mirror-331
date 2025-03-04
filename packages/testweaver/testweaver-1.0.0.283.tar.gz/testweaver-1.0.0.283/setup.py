from setuptools import setup, find_packages

setup(
    name='testweaver', # no kebab-casing, or the import won't work 
    version='1.0.0.283',
    author='Albert Willett Jr',
    author_email='albert.willett2@gmail.com',
    description='A module for generating input handling test cases',
    packages=find_packages(),
    install_requires=[
        "basicfeatureflags",
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.8',
    ],
)