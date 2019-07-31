""" eea.sentry Installer
"""
import os
from os.path import join
from setuptools import setup, find_packages

NAME = 'eea.sentry'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description="Zope/Plone Sentry integration",
      long_description=(
          open("README.rst").read() + "\n" +
          open(os.path.join("docs", "HISTORY.txt")).read()
      ),
      long_description_content_type='text/x-rst',
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: Addon",
          "Framework :: Plone :: 4.3",
          "Framework :: Plone :: 5.1",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
      ],
      keywords='EEA Add-ons Plone Zope',
      author='European Environment Agency: IDM2 A-Team',
      author_email='eea-edw-a-team-alerts@googlegroups.com',
      url='https://github.com/eea/eea.sentry',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
            python_requires="==2.7",
            install_requires=[
          'setuptools',
          'eventlet',
          'raven',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': [
              'plone.app.testing',
          ],
          'zope2': []
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """
      )
