from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
from setuptools import setup

setup(
    name='rutu_packages',
    version='0.0.1',
    long_description=open('README.txt').read(),
    long_description_content_type='text/markdown',  # This should be 'text/markdown', not 'txt/markdown'
    packages=['rutu_packages'],
)
