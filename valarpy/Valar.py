import os
import logging
from typing import Optional

from valarpy import global_connection

pexists = os.path.exists
pfile = os.path.isfile
valarpy_config_env_variable_name = "VALARPY_CONFIG"  # type: str


class Valar:
	"""Simplest way to use valarpy with Peewee.
	Requires an environment variable named VALARPY_CONFIG that points to a JSON config file.
	Ex:
		with Valar():
			import valarpy.model as model
			print(len(model.Projects.select())
	"""
	config_file_path = None  # type: str

	def __init__(self, config_file_path: Optional[str] = None):
		if config_file_path is None:
			if valarpy_config_env_variable_name not in os.environ:
				raise ValueError('Environment variable {} is not set; set this to the correct .json file'.format(valarpy_config_env_variable_name))
			self.config_file_path = os.environ[valarpy_config_env_variable_name]
		else:
			self.config_file_path = config_file_path
		if not pexists(self.config_file_path):
			raise ValueError("{} file {} does not exist".format(valarpy_config_env_variable_name, self.config_file_path))
		if not pfile(self.config_file_path):
			raise ValueError("{} file {} is not a file".format(valarpy_config_env_variable_name, self.config_file_path))

	def open(self) -> None:
		db = global_connection.GlobalConnection.from_json(self.config_file_path)
		db.open()
		db.connect_with_peewee()  # don't worry, this will be closed with the GlobalConnection
		global_connection.db = db  # set a global variable, which peewee will access

	def close(self) -> None:
		logging.info("Closing connection to Valar")
		global_connection.db.close()

	def __enter__(self):
		self.open()
		return self

	def __exit__(self, t, value, traceback):
		self.close()

	def __del__(self):
		self.close()


__all__ = ['Valar', 'global_connection']
