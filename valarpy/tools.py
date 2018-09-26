from warnings import warn
import ast, numbers
from typing import List, Union, Type

import pandas as pd
import peewee
from valarpy.model import BaseModel

from klgists.common import pretty_dict, pp_dict


from valarpy.model import ValarLookupError

warn("Importing valarpy.tools, which is deprecated", DeprecationWarning)

class Tools:

	@staticmethod
	def query(query: peewee.Expression) -> pd.DataFrame:
		return pd.DataFrame([
			pd.Series(row._data)
			for row in query
		])

	@staticmethod
	def describe(thing_class: Type[BaseModel]) -> None:
		pp_dict(thing_class._meta.columns)

	@staticmethod
	def description(thing_class: Type[BaseModel]) -> pd.DataFrame:
		return pd.DataFrame.from_dict(ast.literal_eval(pretty_dict(thing_class._meta.columns)), orient='index').rename(columns={0: 'type'})

	@staticmethod
	def fetch(thing_class: Type[BaseModel], thing: Union[any, int, str], name_column: str = 'name'):
		return thing_class.fetch(thing)

	def fetch_to_query(thing_class: Type[BaseModel], thing: Union[any, int, str], name_column: str = 'name') -> List[peewee.Expression]:
		return thing_class.fetch_to_query(thing)


__all__ = ['Tools']

