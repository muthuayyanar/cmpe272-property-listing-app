import io

from setuptools import find_packages, setup

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='amk-property-listings',
    version='1.0.0',
    url='https://github.com/muthuayyanar/cmpe-272-property-listing-app/',
    license='BSD',
    maintainer='Muthuraja Ayyanar',
    description='Web app built to display property listing data with SSO using Autho for the SJSU CMPE-272 Spring 2019 course.',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'pymongo',
        'jwt',
        'authlib', 
        'python-dotenv',
    ],
    extras_require={
        'test': [
            'mongomock',
            'pytest',
            'pytest-cov',
            'coverage',
        ],
    },
)
