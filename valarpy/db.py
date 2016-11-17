# coding=utf-8

import contextlib
import pymysql
import gists.connected as conned

import warnings
from typing import Dict

_config = None


@property
def config():
	return _config

@config.setter
def get_config(config_dict: Dict[str, str]):
	"""The database connectivity information as a dict.
	:param config_dict: A dictionary containing 'host', 'user', 'password', 'db', and 'port' at a minimum.
	"""
	global _config
	if _config is not None and config_dict != _config:
		warnings.warn("Database connection to Valar was already set and was different!")
	_config = config_dict


def get_url():
	if config is None:
		raise ValueError("The database configuration was not set; first set db.config = a-json-config-file")
	return "mysql://{}:{}@{}:{}/{}".format(config['user'], config['password'], config['host'], config['port'], config['db'])

@contextlib.contextmanager
def connected():
	connection = pymysql.connect(host=config['host'],
								user=config['user'],
								password=config['password'],
								port=config['port'],
								db=config['db'],
								cursorclass=pymysql.cursors.DictCursor)
	with conned.connected(connection):
		global select, execute
		select, execute = conned.select, conned.execute
		yield
