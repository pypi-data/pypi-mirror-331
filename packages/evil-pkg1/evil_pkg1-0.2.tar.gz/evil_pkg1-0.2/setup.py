
import requests


requests.get("http://127.0.0.1:8000/evil")

from setuptools import setup

setup(
    name="evil-pkg1",
    version="0.2",
    packages=["evil_pkg1"],
    description="Just a harmless package :)",
)
