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

### Installation

Locally, which probably isn't needed:

```bash
pip install --install-option="--prefix=$HOME/.local" .
```

From another project in its `requirements.txt`:

```
git+https://github.com/kokellab/valarpy.git@0.1#egg=valarpy
```

Make sure the release (between @ and #) matches what's in [setup.py](setup.py).


### Generating the Peewee model

Use [gen-peewee-model.py](https://github.com/kokellab/kl-tools/blob/master/python/kltools/gen-peewee-model.py):

```bash
gen-peewee-model.py --output valarpy/model.py --host valinor.ucsf.edu --schema ../valar/schema.sql --username mandolin --db kokel
```

This will fix several critical issues that Peewee introduces.
