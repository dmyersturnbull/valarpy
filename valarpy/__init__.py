__author__ = "Douglas Myers-Turnbull"
__copyright__ = "Copyright 2019 Douglas Myers-Turnbull, Kokel Lab, & the University of California, San Francisco"
__credits__ = ["Douglas Myers-Turnbull"]
__license__ = "Apache License, Version 2.0"
__maintainer__ = "Douglas Myers-Turnbull"
__status__ = "Production"
__version__ = "1.4.3"

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
