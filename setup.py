from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in ts_distribution/__init__.py
from ts_distribution import __version__ as version

setup(
	name="ts_distribution",
	version=version,
	description="Distribution",
	author="Tech Station",
	author_email="developers@techstation.com.eg",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
