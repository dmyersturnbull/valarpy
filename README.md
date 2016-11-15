# valarpy
Python code to talk to the Kokel Lab database, Valar. Import this into other projects.

### Example usage

In this example, the JSON file must contain _host_, _user_, _password_, _db_, and _port_. Example are provided in [`config/connection/`](config/).
Note that these are currently temporary but real users. It is essential that you _use the lowest-privileged user possible for your need_; in order, these are:
- [`safe_read_only_user.json`](config/safe_read_only_user.json), _mandolin_ for SELECT only
- [`user_that_can_update.json`](config/user_that_can_update.json), _bassoon_ for SELECT and UPDATE (useful for changing note, description and comment fields, fixing obvious mistakes, and setting _suspicuous_ flags)
- [`user_that_can_insert_update_delete.json`](config/user_that_can_insert_update_delete.json), _harp_ for SELECT, UPDATE, INSERT, and DELETE; avoid using if at all possible

```python
import json
from valarpy import db

# you MUST do this before importing model
with open('config/connection.json') as f:
	db.config = json.load(f)
from model import *

# using the Python Object-Relational Mapping model
for row in StimulusSources:
	print(row['name'])

# using SQL queries directly
with db.connected():
	for stim_name in "SELECT name FROM stimulus_sources":
		print(stim_name)

# another advanced example using SQL
with db.connected():
    query = "SELECT name, chemspider_id FROM compounds WHERE compounds.inchikey = %s"
    for row in db.select(query, 'IAZDPXIOMUYVGZ-UHFFFAOYSA-N'):
        print(row)
```

See [more examples](https://github.com/kokellab/kokel-scripts) or the [Peewee documentation](http://docs.peewee-orm.com/en/latest/) for further information.

**A word of caution:** constructing an object in model.py will add a row to the database. For example, this will attempt to add a new Well to an existing plate:

```python
compound = Well(0, -1, 1)
```

In this case, it will fail because the object is ill-formed (for example, -1 is negative and doesn't match an entry in __plate_runs__.

### Installation

Locally, which probably isn't needed:

```bash
pip install --install-option="--prefix=$HOME/.local" .
```

From another project in its `requirements.txt`:

```
-e git+https://github.com/kokellab/valarpy.git@0.1#egg=valarpy
```

Make sure the release (between @ and #) matches what's in [setup.py](setup.py).


### Generating the Peewee model

```bash
python -m pwiz -e mysql -H 169.230.182.91 -u mandolin -P kokel > model.py
```

After doing this, replace the top with:

```python
from peewee import *

from .db import config

database = MySQLDatabase(config['db'], **{'user': config['user'], 'password': config['password'], 'host': config['host'], 'port': config['port']})

```

Also convert binary fields to type `BlobField`; Peewee used `CharField` for MariaDB fields of type `binary` `varbinary` and `TextField` for fields of type `blob` and its variants.

