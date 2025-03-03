# coding=utf8
""" Mouth

Handles communication
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__copyright__	= "Ouroboros Coding Inc."
__email__		= "chris@ouroboroscoding.com"
__created__		= "2022-12-12"

# Ouroboros imports
from config import config
from upgrade import upgrade

# Python imports
from os.path import abspath, expanduser
from pathlib import Path
from sys import argv, exit, stderr

# Pip imports
from rest_mysql import Record_MySQL

# Module imports
from mouth import install, rest

def cli():
	"""CLI

	Called from the command line to run from the current directory

	Returns:
		uint
	"""

	# Get Mouth config
	conf = config.mouth({
		'data': './.mouth',
		'records': 'primary'
	})
	if '~' in conf['data']:
		conf['data'] = expanduser(conf['data'])
	conf['data'] = abspath(conf['data'])

	# Add the global prepend
	Record_MySQL.db_prepend(config.mysql.prepend(''))

	# Add the primary mysql DB
	Record_MySQL.add_host('mouth', config.mysql.hosts[conf['records']]({
		'host': 'localhost',
		'port': 3306,
		'charset': 'utf8',
		'user': 'root',
		'passwd': ''
	}))

	# If we have no arguments
	if len(argv) == 1:

		# Run the REST server
		return rest.run()

	# Else, if we have one argument
	elif len(argv) == 2:

		# If we are installing
		if argv[1] == 'install':
			return install.install(
				conf['data'],
				Path(__file__).parent.resolve()
			)

		# Else, if we are explicitly stating the rest service
		elif argv[1] == 'rest':
			return rest.run()

		# Else, if we are upgrading
		elif argv[1] == 'upgrade':
			return upgrade(
				conf['data'],
				Path(__file__).parent.resolve()
			)

	# Else, arguments are wrong, print and return an error
	print('Invalid arguments', file=stderr)
	return 1

# Only run if called directly
if __name__ == '__main__':
	exit(cli())