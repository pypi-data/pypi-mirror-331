
import requests


requests.get("http://127.0.0.1:8000/evil")

from setuptools import setup

setup(
    name="evil-pkg2",
    version="0.3",
    packages=["evil_pkg2"],
    description="Just a harmless package :)",
)
