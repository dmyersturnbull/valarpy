# valarpy
Python code to talk to the Kokel Lab database, Valar. Import this into other projects.

### Example usage

In this example, the JSON file must contain _host_, _user_, _password_, _db_, and _port_. An example is provided in [`config/connection.json`](config/connection.json).

```python
import json
from valarpy import db
import model

with open('config/connection.json') as f:
	db.config = json.read(f)

# using the Python Object-Relational Mapping model
for row in model.StimulusSources:
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
compound = model.Well(0, -1, 1)
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
