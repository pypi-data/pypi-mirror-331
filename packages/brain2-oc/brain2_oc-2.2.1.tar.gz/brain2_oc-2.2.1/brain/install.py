# coding=utf8
""" Install

Method to install the necessary brain tables
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2023-07-12"

# Ouroboros imports
from upgrade import set_latest

# Module imports
from brain import records
from brain.helpers import access, users

def install(conf):
	"""Install

	Installs required files, tables, records, etc. for the service

	Arguments:
		conf (dict): The brain config

	Returns:
		int
	"""

	# Install tables
	records.install()

	# If we don't have an admin
	if not records.User.filter(
		{ 'email': 'admin@localhost' },
		raw = ['_id'],
		limit = 1
	):

		# Install admin
		oUser = records.User({
			'email': 'admin@localhost',
			'passwd': records.User.password_hash('Admin123'),
			'locale': conf['user_default_locale'],
			'first_name': 'Admin',
			'last_name': 'Istrator'
		})
		sUserId = oUser.create(changes = { 'user': users.SYSTEM_USER_ID })

		# Add admin permissions
		records.Permission.create_many([
			records.Permission({
				'_user': sUserId,
				'_portal': '',
				'name': 'brain_user',
				'id': users.RIGHTS_ALL_ID,
				'rights': access.C | access.R | access.U
			}),
			records.Permission({
				'_user': sUserId,
				'_portal': '',
				'name': 'brain_permission',
				'id': users.RIGHTS_ALL_ID,
				'rights': access.R | access.U
			})
		])

	# Store the last known upgrade version
	set_latest(conf['data'], conf['module'])

	# Return OK
	return 0