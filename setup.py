from setuptools import setup
import os

if os.system("bash install.sh") != 0:
    raise RuntimeError("install.sh failed")

setup(
    name="ai-readability",
    version="0.1",
    install_requires=[],
)
