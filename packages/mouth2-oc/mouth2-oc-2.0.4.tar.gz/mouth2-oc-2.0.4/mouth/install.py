# coding=utf8
""" Install

Method to install the necessary mouth tables
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2024-12-14"

# Ouroboros imports
from upgrade import set_latest

# Module imports
from mouth import records

def install(path: str, module: str):
	"""Install

	Installs required files, tables, records, etc. for the service

	Arguments:
		path (str): The path to the version file
		module (str): The name of the version's module

	Returns:
		int
	"""

	# Install tables
	records.install()

	# Store the last known upgrade version
	set_latest(path, module)

	# Return OK
	return 0