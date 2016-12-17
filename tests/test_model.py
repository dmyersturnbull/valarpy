# coding=utf-8

# TODO this isn't a real test

import valarpy.global_connection as global_connection

def do_my_stuff():
	for row in Users.select():
		print(row.__dict__)

def do_my_stuff2():
	for row in db.select("SELECT username from users where first_name=%s", 'cole'):
		print(row)

with global_connection.GlobalConnection.from_json('../config/real_config.json') as db:
	db.connect_with_peewee()
	global_connection.db = db
	from valarpy.model import *
	do_my_stuff()
	#db.connect_raw()
	#do_my_stuff()
