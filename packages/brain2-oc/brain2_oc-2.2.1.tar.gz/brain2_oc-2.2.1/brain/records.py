# coding=utf8
""" Brain Records

Handles the record structures for the Authorization service
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__maintainer__	= "Chris Nasr"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2022-03-20"

# Limit exports
__all__ = [ 'cache', 'install', 'Key', 'Permissions', 'User', 'Verify' ]

# Ouroboros imports
from body.constants import SECONDS_HOUR
from config import config
import jsonb
from define import Parent, Tree
from rest_mysql import Record_MySQL
from strings import random

# Python imports
from hashlib import sha1
import re
import pathlib
from typing import Literal

# Module variable
_moRedis = None

# Get the definitions path
_defPath = '%s/definitions' % pathlib.Path(__file__).parent.resolve()

def cache(redis=None):
	"""Cache

	Get/Set the cache instance

	Arguments:
		redis (StrictRedis): The instance to set, None for getting

	Returns:
		None|StrictRedis
	"""
	global _moRedis
	if not redis:
		return _moRedis
	else:
		_moRedis = redis

def install():
	"""Install

	Handles the initial creation of the tables in the DB

	Returns:
		None
	"""
	Key.table_create()
	Permission.table_create()
	User.table_create()

class Key(Record_MySQL.Record):
	"""Key

	Represents a key for email verification, forgotten password, etc.

	Extends:
		Record_MySQL.Record
	"""

	_conf = None
	"""Configuration"""

	@classmethod
	def config(cls):
		"""Config

		Returns the configuration data associated with the record type

		Returns:
			dict
		"""

		# If we haven't loaded the config yet
		if not cls._conf:
			cls._conf = Record_MySQL.Record.generate_config(
				Tree.from_file('%s/key.json' % _defPath),
				override={'db': config.mysql.db('brain')}
			)

		# Return the config
		return cls._conf

class Permission(Record_MySQL.Record):
	"""Permission

	Represents a single group of permissions associated with a user

	Extends:
		Record_MySQL.Record
	"""

	_conf = None
	"""Configuration"""

	_tree_key = 'perms:%s%s'
	"""The template used to generate the tree cache keys"""

	@classmethod
	def config(cls):
		"""Config

		Returns the configuration data associated with the record type

		Returns:
			dict
		"""

		# If we haven't loaded the config yet
		if not cls._conf:
			cls._conf = Record_MySQL.Record.generate_config(
				Tree.from_file('%s/permission.json' % _defPath),
				override={'db': config.mysql.db('brain')}
			)

		# Return the config
		return cls._conf

	@classmethod
	def portal_tree(cls, id_portal: tuple) -> dict:
		"""User Tree

		Returns the tree

		Arguments:
			id_portal (tuple): The ID and portal of the permissions

		Returns:
			dict
		"""

		global _moRedis

		# If we got a single id
		if isinstance(id_portal, tuple):

			# Try to fetch it from the cache
			sPermissions = _moRedis.get(cls._tree_key % id_portal)

			# If it's found
			if sPermissions:

				# If it's -1
				if sPermissions == b'-1':
					return None

				# Decode and return the data
				return jsonb.decode(sPermissions)

			# Else, permissions not found in cache, fetch and return them from
			#	the db
			else:
				return cls.portal_tree_reset(id_portal)

		# Else, we got multiple IDs
		else:

			# Fetch multiple keys
			lPermissions = _moRedis.mget([
				cls._tree_key % t for t in id_portal
			])

			# Go through each one
			for i, t in enumerate(id_portal):

				# If we have a record
				if lPermissions[i]:

					# If it's -1
					if lPermissions[i] == b'-1':
						lPermissions[i] = None

					# Else, decode it
					else:
						lPermissions[i] = jsonb.decode(lPermissions[i])

				else:

					# Fetch the records from the DB
					lPermissions[i] = cls.portal_tree_reset(t)

					# Store it in the cache
					_moRedis.set(
						cls._tree_key % t,
						jsonb.encode(lPermissions[i])
					)

			# Return the permissions
			return lPermissions

	@classmethod
	def portal_tree_clear(cls, id_portal: list | tuple):
		"""Portal Tree Clear

		Removes permissions from the cache by ID

		Arguments:
			id_portal (tuple|tuple[]): One or more tuples with the ID of the \
			user and the portal
		"""

		# If we got one id, delete the one key
		if isinstance(id_portal, tuple):
			_moRedis.delete(cls._tree_key % id_portal)

		# Else, delete multiple keys if we didn't just get an empty list
		elif id_portal:
			_moRedis.delete(*[ cls._tree_key % t for t in id_portal ])

	@classmethod
	def portal_tree_reset(cls, id_portal: tuple) -> dict:
		"""User Tree Rest

		Resets the user's portal tree in the cache and returns it for anyone \
		who needs it

		Arguments:
			user (tuple): The ID and portal of the permissions

		Returns:
			dict
		"""

		global _moRedis

		# Fetch the records from the DB
		lPermissions = cls.filter({
			'_user': id_portal[0],
			'_portal': id_portal[1]
		}, raw = [ 'name', 'id', 'rights' ] )

		# If there's none
		if not lPermissions:

			# Do we have a user?
			if not User.exists(id_portal[0]):

				# Store it for an hour to avoid bad actors
				_moRedis.setex(
					cls._tree_key % id_portal, '-1', SECONDS_HOUR
				)

				# Return nothing
				return None

		# Init the tree
		dTree = {}

		# Loop through the records to generate the tree
		for d in lPermissions:

			# If the name exists
			if d['name'] in dTree:
				dTree[d['name']][d['id']] = d['rights']
			else:
				dTree[d['name']] = { d['id']: d['rights'] }

		# Store it in the cache
		_moRedis.set(
			cls._tree_key % id_portal,
			jsonb.encode(dTree)
		)

		# Return the tree
		return dTree

class User(Record_MySQL.Record):
	"""User

	Represents a single user in the micro services system

	Extends:
		Record_MySQL.Record
	"""

	_conf = None
	"""Configuration"""

	@classmethod
	def cache(cls, _id, raw=False, custom={}):
		"""Cache

		Fetches the Users from the cache and returns them

		Arguments:
			_id (str|str[]): The ID(s) to fetch
			raw (bool): Return raw records or Users
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			User|User[]|dict|dict[]
		"""

		global _moRedis

		# If we got a single ID
		if isinstance(_id, str):

			# Fetch a single key
			sUser = _moRedis.get(_id)

			# If we have a record
			if sUser:

				# Decode it
				dUser = jsonb.decode(sUser)

			else:

				# Fetch the record from the DB
				dUser = cls.get(_id, raw=True, custom=custom)

				# Store it in the cache
				_moRedis.set(_id, jsonb.encode(dUser))

			# If we don't have a record
			if not dUser:
				return None

			# If we want raw
			if raw:
				return dUser

			# Return an instance
			return cls(dUser)

		# Else, fetch multiple
		else:

			# Fetch multiple keys
			lUsers = _moRedis.mget([k for k in _id])

			# Go through each one
			for i in range(len(_id)):

				# If we have a record
				if lUsers[i]:

					# Decode it
					lUsers[i] = jsonb.decode(lUsers[i])

				else:

					# Fetch the record from the DB
					lUsers[i] = cls.get(_id[i], raw=True, custom=custom)

					# Store it in the cache
					_moRedis.set(_id[i], jsonb.encode(lUsers[i]))

			# If we want raw
			if raw:
				return lUsers

			# Return instances
			return [d and cls(d) or None for d in lUsers]

	@classmethod
	def clear(cls, _id):
		"""Clear

		Removes a user from the cache

		Arguments:
			_id (str): The ID of the user to remove

		Returns:
			None
		"""

		# Delete the key in Redis
		_moRedis.delete(_id)

	@classmethod
	def config(cls):
		"""Config

		Returns the configuration data associated with the record type

		Returns:
			dict
		"""

		# If we haven't loaded the config yet
		if not cls._conf:
			cls._conf = Record_MySQL.Record.generate_config(
				Tree.from_file('%s/user.json' % _defPath),
				override={'db': config.mysql.db('brain')}
			)

		# Return the config
		return cls._conf

	@staticmethod
	def password_hash(passwd):
		"""Password Hash

		Returns a hashed password with a unique salt

		Arguments:
			passwd (str): The password to hash

		Returns:
			str
		"""

		# Generate the salt
		sSalt = random(32, ['0x'])

		# Generate the hash
		sHash = sha1(sSalt.encode('utf-8') + passwd.encode('utf-8')).hexdigest()

		# Combine the salt and hash and return the new value
		return sSalt[:20] + sHash + sSalt[20:]

	@classmethod
	def password_strength(cls, passwd):
		"""Password Strength

		Returns true if a password is secure enough

		Arguments:
			passwd (str): The password to check

		Returns:
			bool
		"""

		# If we don't have enough or the right chars
		if 8 > len(passwd) or \
			re.search('[A-Z]+', passwd) == None or \
			re.search('[a-z]+', passwd) == None or \
			re.search('[0-9]+', passwd) == None:

			# Invalid password
			return False

		# Return OK
		return True

	def password_validate(self, passwd):
		"""Password Validate

		Validates the given password against the current instance

		Arguments:
			passwd (str): The password to validate

		Returns:
			bool
		"""

		# Get the password from the record
		sPasswd = self.field_get('passwd')

		# Split the password
		sSalt = sPasswd[:20] + sPasswd[60:]
		sHash = sPasswd[20:60]

		# Return OK if the re-hashed password matches
		return sHash == sha1(
			sSalt.encode('utf-8') + passwd.encode('utf-8')
		).hexdigest()

	@classmethod
	def simple_search(cls, query, custom={}):
		"""Simple Search

		Looks for query in multiple fields

		Arguments:
			query (str): The query to search for
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			str[]
		"""

		# Get the structure
		dStruct = cls.struct(custom)

		# Generate the SQL
		sSQL = "SELECT `_id`\n" \
				"FROM `%(db)s`.`%(table)s`\n" \
				"WHERE `first_name` LIKE '%%%(query)s%%'\n" \
				"OR `last_name` LIKE '%%%(query)s%%'\n" \
				"OR CONCAT(`first_name`, ' ', `last_name`) LIKE '%%%(query)s%%'\n" \
				"OR `email` LIKE '%%%(query)s%%'\n" \
				"OR `phone_number` LIKE '%%%(query)s%%'" % {
			'db': dStruct['db'],
			'table': dStruct['table'],
			'query': Record_MySQL.Commands.escape(dStruct['host'], query)
		}

		# Run the search and return the result
		return Record_MySQL.Commands.select(
			dStruct['host'],
			sSQL,
			Record_MySQL.ESelect.COLUMN
		)

Verify = Parent.from_file('%s/verify.json' % _defPath)
"""Used to validate verify calls from the outside"""