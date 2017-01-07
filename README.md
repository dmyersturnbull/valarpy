# [valarpy](https://github.com/kokellab/valarpy)
Python code to talk to the Kokel Lab database, [Valar](https://github.com/kokellab/valar). Import this into other projects.

### configuration

An example configuration file is at [config/example_config.json](config/example_config.json). 
You'll need to fill in the username and password for the database and SSH connection. In other words, ask Douglas for access. _**Do not** put a username and/or password anywhere that's web-accessible (including Github), with the exception of a password manager with 2-factor authentication._


### example usage with Peewee

```python

import valarpy.global_connection as global_connection

def do_my_stuff():
	for row in Users.select():
		print(row.username)

with global_connection.GlobalConnection.from_json('../config/real_config.json') as db:
	db.connect_with_peewee()     # don't worry, this will be closed with the GlobalConnection
	global_connection.db = db    # set a global variable, which peewee will access
	from valarpy.model import *  # you MUST import this AFTER setting global_connection.db
	do_my_stuff()
```

### example usage with plain SQL

```python

import valarpy.global_connection as global_connection

def do_my_stuff():
	for row in db.select("SELECT username from users where first_name=%s", 'cole'):
		print(row)

with global_connection.GlobalConnection.from_json('../config/real_config.json') as db:
	db.connect_with_raw_sql()
	global_connection.db = db    # you don't actually need to set this here
	do_my_stuff()
```

See [more examples](https://github.com/kokellab/kokel-scripts) or the [Peewee documentation](http://docs.peewee-orm.com/en/latest/) for further information.

### installation

Install using:

```
pip install git+https://github.com/kokellab/valarpy.git@0.2#egg=valarpy
```

Make sure the release (between @ and #) matches what's in [setup.py](setup.py).
You can also add it to another project's `requirements.txt`:

```
git+https://github.com/kokellab/valarpy.git@0.3#egg=valarpy
```

Alternatively, you can install it locally. This probably isn't needed:

```bash
pip install --install-option="--prefix=$HOME/.local" .
```


### generating the Peewee model

Use [gen-peewee-model.py](https://github.com/kokellab/kl-tools/blob/master/python/kltools/gen-peewee-model.py):

```bash
ssh -L 14430:localhost:3306 username@valinor.ucsf.edu
gen-peewee-model.py --output valarpy/model.py --host 127.0.0.1 --schema ../valar/schema.sql --username username --db valar --port 14430 --header-file config/header-lines.txt
```

This will fix several critical issues that Peewee introduces.
Fix the indentation to use tabs in an editor before committing the change—otherwise the diff will be hard to read.
