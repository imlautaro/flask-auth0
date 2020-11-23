"""
Flask-Auth0
-----------
An easy way to protect your API with Auth0
"""

from setuptools import setup

setup(
    name='Flask-Auth0',
    version='1.0',
    url='https://github.com/imlautaro/flask-auth0',
    license='MIT',
    author='Lautaro Pereyra',
    author_email='dev.lautaropereyra@gmail.com',
    description='An easy way to protect your API with Auth0',
    py_modules=['flask_auth0'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    python_requires=">= 3.6",
    install_requires=[
        'flask',
        'six',
        'python-jose'
    ]
)
