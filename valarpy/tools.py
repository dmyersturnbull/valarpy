
import json, sys, ast
from datetime import date, datetime
from typing import List, Callable, Any, Union, Optional, Dict

import pandas as pd
import peewee
from hurry.filesize import size as _hurrysize

from klgists.common import json_serial, pretty_dict, pp_dict

class ValarLookupError(KeyError): pass

class Tools:

	@staticmethod
	def query(query: peewee.Expression) -> pd.DataFrame:
		return pd.DataFrame([
			pd.Series(row._data)
			for row in query
		])

	@staticmethod
	def describe(thing_class: peewee.Model) -> None:
		pp_dict(thing_class._meta.columns)

	@staticmethod
	def description(thing_class: peewee.Model) -> None:
		return pd.DataFrame.from_dict(ast.literal_eval(pretty_dict(thing_class._meta.columns)), orient='index').rename(columns={0: 'type'})

	@staticmethod
	def fetch(thing_class: peewee.Model, thing: Union[any, int, str], name_column: str = 'name'):
		if isinstance(thing, peewee.Model):
			found = thing
		elif isinstance(thing, int):
			found = thing_class.select().where(thing_class.id == thing).first()
		elif isinstance(thing, str) and hasattr(thing_class, name_column):
			found = thing_class.select().where(getattr(thing_class, name_column) == thing).first()
		else:
			raise TypeError("Invalid type for {} in {}".format(thing, thing_class))
		if found is None:
			raise ValarLookupError("Could not find {} in {}".format(thing, thing_class))
		return found

	def fetch_to_query(thing_class: peewee.Model, thing: Union[any, int, str], name_column: str = 'name') -> List[peewee.Expression]:
		if isinstance(thing, (int, str, thing_class)):
			return [thing_class.id == Tools.fetch(thing_class, thing, name_column=name_column).id]
		elif isinstance(thing, List):
			return thing
		elif isinstance(thing, peewee.Expression):
			return [thing]
		else:
			raise TypeError("Invalid type for {} in {}".format(thing, thing_class))


__all__ = ['Tools']

