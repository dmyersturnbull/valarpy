"""
Part of Valarpy by the Kokel Lab.
This module provides a way to connect to and load Valar.
See the `Valar` class.
"""
import os
import logging
from pathlib import Path
from typing import Union
from valarpy import global_connection

def _get_existing_path(*paths):
	paths = [None if p is None else Path(p) for p in paths]
	for path in paths:
		if path is not None and path.exists(): return path
CONFIG_PATH = _get_existing_path(
	os.environ.get('VALARPY_CONFIG'),
	Path.home() / '.valarpy' / 'config.json',
	Path.home() / '.valarpy' / 'read_only.json'
)
if not CONFIG_PATH.exists():
	raise KeyError("Valarpy config is not set. Set VALARPY_CONFIG as an environment variable and make sure it exists.")


class Valar:
	"""
	Simplest way to use valarpy with Peewee.
	Requires an environment variable named VALARPY_CONFIG that points to a JSON config file.
	Ex:
		>>> with Valar():
		>>>	import valarpy.model as model
		>>>	print(len(model.Projects.select())
	"""

	def __init__(self, config_file_path: Union[None, str, Path] = None):
		self.config_file_path = CONFIG_PATH if config_file_path is None else Path(config_file_path)

	def reconnect(self):
		self.close()
		self.open()

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


def main():
	"""Entry point to test connection."""
	with Valar():
		from valarpy.model import Refs
		print("Connection successful")
		print("Found {} refs".format(len(list(Refs.select()))))
if __name__ == '__main__':
	main()


__all__ = ['Valar', 'global_connection']
