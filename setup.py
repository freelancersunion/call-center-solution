#!/usr/bin/env python
from setuptools import setup, find_packages

required_modules = [
                    "amqplib",
                    "django == 1.1.1"
                    ]


setup(
      name="callcenter_solution",
      version="0.1",
      description="This is a simple MQ based call center solution, useable in disaster recovery situations. Relies on Rabbit MQ and django for webservices as well as database ORM. MQ, Webservice, and ORM can be easily changed. ",
      author="Vikash Dat",
      author_email="vdat@freelancersunion.org",
      url=" http://repositories.fuwt/svn/ivr_call_center_DR/",
      packages=find_packages(exclude=['tests']),      
      install_requires=required_modules
     )