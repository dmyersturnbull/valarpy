#!/usr/bin/env python
# coding=utf-8

import re
import os
import sys
import argparse
import subprocess
import fileinput
import peewee
import logging
from typing import List, Set

blob_regex = re.compile("^ *\`([^ ]+)\` (?:(?:binary)|(?:[[a-zA-Z]*blob)).*$")
peewee_field_regex = re.compile('^ *([a-z][a-z0-9_]*) = ([A-Z][A-Za-z]*Field)\(.*\)$')
type_regex = re.compile('[A-Z][A-Za-z]*Field')

def _lines(filename: str):
	with open(filename, 'r') as f:
		for line in f: yield line.rstrip('\n\r')

def gen_model(username: str, db: str, output: str):
	with open(output, 'w') as f:
		subprocess.call([sys.executable, '-m', 'pwiz', '-e', 'mysql', '-H', 'valinor.ucsf.edu', '-u', username, '-P', db], stdout=f)

def fix_connection(output: str):
	for line in fileinput.input(output, inplace=True):
		if fileinput.filelineno() == 1:
			print("from peewee import *")
		elif fileinput.filelineno() == 2:
			print("from .db import config")
		elif fileinput.filelineno() == 3:
			print("database = MySQLDatabase(config['db'], **{'user': config['user'], 'password': config['password'], 'host': config['host'], 'port': config['port']})")
		else:
			print(line.rstrip())

def find_blob_columns(schema: str) -> Set[str]:
	"""Returns the names of columns that have binary or *blob types."""
	return {m.group(1) for m in [blob_regex.match(line) for line in _lines(schema)] if m is not None}

def fix_blobs(columns: Set[str], output: str):
	for line in fileinput.input(output, inplace=True):
		m = peewee_field_regex.match(line)
		if m is not None and m.group(1) in columns:
			print(type_regex.sub('BlobField', line.rstrip()) + '  # auto-corrected to BlobField')
		else:
			print(line.rstrip())

def main(opts: List[str]):
	gen_model(opts.username, opts.db, opts.output)
	fix_connection(opts.output)
	blob_columns = find_blob_columns(opts.schema)
	logging.info("Fixing columns {}".format(blob_columns))
	fix_blobs(blob_columns, opts.output)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Generates a peewee model and fixes the connection info and binary/blob columns.')
	parser.add_argument('--output', default='model-auto-generated.py', type=str, help='Output model.py file')
	parser.add_argument('--username', required=True, type=str, help='The database username')
	parser.add_argument('--db', required=True, type=str, help='The name of the database')
	parser.add_argument('--schema', required=True, type=str, help='The path to the schema .sql file; must be for this database ONLY')
	opts = parser.parse_args()
	main(opts)

