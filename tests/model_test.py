import unittest, os

from valarpy.Valar import Valar
valar = Valar(os.environ['VALARPY_CONFIG'])
valar.open()
from valarpy.model import *


class ModelTest(unittest.TestCase):

	def test_data(self):
		self.assertEquals(Users(id=99, username='test')._data, {'id': 99, 'username': 'test'})


if __name__ == ['__main__']:
	unittest.main()
