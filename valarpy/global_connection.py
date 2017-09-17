import os
import json
import logging
from typing import Dict, Union
from valarpy.connection import Connection

db = None

class GlobalConnection(Connection):

	@classmethod
	def from_json(cls, config_path: str):
		if os.path.isfile(config_path) and os.access(config_path, os.R_OK):
			logging.info("Using Valar connection from '{}'".format(config_path))
			with open(config_path) as jscfg:
				params = json.load(jscfg)  # type: Dict[str, Union[str, int, None]]
				return cls(**params)
		else:
			raise ValueError("{} does not exist, is not a file, or is not readable".format(config_path))

	@classmethod
	def from_dict(cls, dct: Dict[str, str]):
		return cls(**dct)
