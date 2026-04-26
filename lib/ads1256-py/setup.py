#!/usr/bin/python3

from distutils.core import setup, Extension

ads1256 = Extension('ads1256',
                    sources = ['src/ads1256-py.c'],
		    libraries = ['ads1256'])

setup (name = 'ADS1256',
       version = '0.1',
       description = 'Package for interfacing with an ADS1256 to perform analog conversions',
       ext_modules = [ads1256])
