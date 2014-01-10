import os
from setuptools import setup

setup(
    name = "baketu",
    version = "0.1",
    url = "https://github.com/tengu/py-baketu",
    description = "manage buckets in key-value store",
    packages = ['baketu'],
    entry_points={"console_scripts": [ 'baketu=baketu:main' ]},
    install_requires=['boto', 'baker'],
    zip_safe=False,
)
