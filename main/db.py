# coding=utf-8

import contextlib
import pymysql
import gists.connected as conned

import os
import json

# this line makes me officially hate Python (and with a passion)
# paths are always relative to the working dir
# join this filename's parent with 'config' and then with 'connection.json'
f = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'), 'connection.json')
with open(f) as f:
    config = json.load(f)
    url = "mysql://{}:{}@{}:{}/{}".format(config['user'], config['password'], config['host'], config['port'],
                                          config['db'])


@contextlib.contextmanager
def connected():
    connection = pymysql.connect(host=config['host'],
                                 user=config['user'],
                                 password=config['password'],
                                 port=config['port'],
                                 db=config['db'],
                                 cursorclass=pymysql.cursors.DictCursor)
    with conned.connected(connection):
        global select, execute
        select, execute = conned.select, conned.execute
        yield
