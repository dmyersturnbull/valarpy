# [valarpy](https://github.com/kokellab/valarpy)
Python code to talk to the Kokel Lab database, [Valar](https://github.com/kokellab/valar). Import this into other projects.

There is more documentation available in the Valar readme, including an [Entity–Relationship Diagram](https://github.com/kokellab/valar/blob/alttables/docs/erd/valar\_schema.png), where the lines are [foreign keys](https://en.wikipedia.org/wiki/Foreign_key) whose targets are denoted as forks.

### configuration

An example configuration file is at [config/example_config.json](config/example_config.json). 
I recommend downloading it to `$HOME/valarpy_configs/read_only.json`
You’ll need to fill in the username and password for the database connection. In other words, ask Douglas for access. _**Do not** put a username and/or password anywhere that’s web-accessible (including Github), with the exception of a password manager with 2-factor authentication._
In addition, you’ll also need to set up SSH keys for Valinor.

Valarpy connects to Valar through an SSH tunnel; the database is not accessible remotely.
There are two modes of connection: Valarpy can either use an existing SSH tunnel or create its own.

##### existing tunnel

Replacing _53419_ with a number of your choosing, create the tunnel using:
```bash
ssh -L 53419:localhost:3306 valinor.ucsf.edu
```
Note that after running it your shell is now on Valinor. You will need to leave this tunnel open while connecting to Valar.
Update your config file, replacing `ssh_host: "valinor.ucsf.edu"` with `local_bind_port: 53419`.
You can of course alias in your `~/.zshrc`. You can add a `valinor-tunnel` alias by running:
```bash
echo "export valinor_tunnel_port=53419" >> ~/.zshrc
echo "alias valinor-tunnel='ssh -L $valinor_tunnel_port:localhost:3306 valinor.ucsf.edu'" >> ~/.zshrc
```

This mode will allow you to use the same tunnel with other languages and to connect to Valar natively.
For example, you can connect to MariaDB from a local terminal using:
```bash
mysql -u dbusername -P $valinor_tunnel_port -p
```

##### new tunnel

If you only use Python, this is slightly preferable because it randomizes the tunnel port. That’s a very minor security benefit, however.
For this mode, just leave `ssh_host: "valinor.ucsf.edu"`


### simplest example

```python
from valarpy.Valar import Valar

with Valar():
# you MUST import this AFTER setting global_connection.db
	from valarpy.model import *
	print("# of projects: {}".format(len(Projects.select())))
```

The sections below show more flexible usage.

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

### running in Jupyter notebooks

Jupyter notebooks seem to drop the connection after the first cell. To resolve this, you can avoid using a `with` statement by using:

```python

db = global_connection.GlobalConnection.from_json('/home/dmyerstu/desktop/valar.json')
db.open()
db.connect_with_peewee()     # don't worry, this will be closed with the GlobalConnection
global_connection.db = db    # set a global variable, which peewee will access
from valarpy.model import *  # you MUST import this AFTER setting global_connection.db

# do whatever till the end of the notebook
```

The database connection and SSH tunnels will hopefully be closed when Jupyter exits. You can also close bith using `db.close()`.

### notes about tables

Assay frames and features (such as MI) are stored as MySQL binary `blob`s.

Each frame in `assay_frames` is represented as a single big-endian unsigned byte. To convert back, use `utils.blob_to_byte_array(blob)`, where `blob` is the Python `bytes` object returned directly from the database.

Each value in `well_features` (each value is a frame for features like MI) is represented as 4 consecutive bytes that constitute a single big-endian unsigned float (IEEE 754 `binary32`). Use `utils.blob_to_float_array(blob)` to convert back.

There shouldn't be a need to insert these data from Python, so there's no way to convert in the forwards direction.

### installation

Install using:

```
pip install git+https://github.com/kokellab/valarpy.git@0.4.1#egg=valarpy
```

Make sure the release (between @ and #) matches what's in [setup.py](setup.py).
You can also add it to another project's `requirements.txt`:

```
git+https://github.com/kokellab/valarpy.git@0.4.1#egg=valarpy
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
