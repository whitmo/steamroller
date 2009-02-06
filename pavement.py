try:
    from paver.virtual import bootstrap
except :
    # minilib does not support bootstrap
    pass

from setuptools import find_packages
from paver.defaults import options, Bunch
from paver.defaults import task, sh, needs
#import sys
#import os

setup_deps = []

install_requires=[
    "zc.buildout",
    "PasteScript",
    "zc.recipe.egg",
    "hexagonit.recipe.cmmi",
    'nose',
    'pip',
    'virtualenv',
    'setuptools>0.6c8'
    ]

virtualenv = Bunch(
        script_name="roller_env.py",
        packages_to_install=install_requires + setup_deps,
        )

version = '0.0'

install_bunch = Bunch(name='steamroller',
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

options(setup=install_bunch,
        virtualenv=virtualenv)

## from setuptools.depends import Require
## pip = Require('pip','',)
## import pdb;pdb.set_trace()
## pip.get_version()

