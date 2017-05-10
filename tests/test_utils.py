import unittest


class TestModel(unittest.TestCase):

	def test_select(self):
		len(Features.select()) > 0
