import os
import unittest

import valarpy.global_connection as global_connection

db = global_connection.GlobalConnection.from_json(os.environ['VALARPY_CONFIG'])
db.open()
db.connect_with_peewee()     # don't worry, this will be closed with the GlobalConnection
global_connection.db = db    # set a global variable, which peewee will access
from valarpy.model import *  # you MUST import this AFTER setting global_connection.db


class TestModel(unittest.TestCase):

	def test_select(self):
		len(Features.select()) > 0
