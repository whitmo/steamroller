from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='steamroller',
      version=version,
      description="tools to help with working with paver",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='disutils build',
      author='whit',
      author_email='whit@opengeo.org',
      url='http://docs.opengeo.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
