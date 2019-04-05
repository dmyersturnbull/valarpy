__version__ = '1.2.0'

valarpy_version = __version__

import peewee
import pandas as pd


class ValarpyTools:
	@staticmethod
	def query(query: peewee.Expression) -> pd.DataFrame:
		return pd.DataFrame([
			pd.Series(row._data)
			for row in query
		])


__all__ = ['__version__', 'valarpy_version', 'ValarpyTools']
