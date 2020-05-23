Guide
====================================

set up SSH keys
---------------

Set up your SSH keys as described in `How To Set Up SSH Keys \|
DigitalOcean <https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2>`__.
You will temporarily need password authentication for this step; ask
Douglas to enable this for you.

1. Run ``ssh-keygen -t rsa`` (and hit enter without using a passphrase)
2. Enter file in which to save the key (``/home/demo/.ssh/id_rsa``):
3. Run ``ssh-copy-id yourname@valinor.ucsf.edu`` to let Valinor know who
   you are
4. Open the file ``~/.ssh/config`` in a text editor, and include these
   lines (deleting any duplicate sections):

::

   Host valinor valinor.ucsf.edu
   HostName valinor.ucsf.edu
   IdentityFile ~/.ssh/id_rsa
   User <yourusername>

   Host github github.com
   HostName github.com
   IdentityFile ~/.ssh/github-rsa
   User <your-github-email-address>

replace User info including ‘<…>’

You can now type ``ssh valinor`` or ``ssh valinor.ucsf.edu`` to log in
without a password.


connect to Valinor
------------------

An example configuration file is at
`config/example_config.json <config/example_config.json>`__. I recommend
downloading it to ``$HOME/valarpy_configs/read_only.json`` You’ll need
to fill in the username and password for the database connection. In
other words, ask Douglas for access. **Do not**\ *put a username and/or
password anywhere that’s web-accessible (including Github), with the
exception of a password manager with 2-factor authentication.* In
addition, you’ll also need to set up SSH keys for Valinor.

Valarpy connects to Valar through an SSH tunnel; the database is not
accessible remotely. There are two modes of connection: Valarpy can
either use an existing SSH tunnel or create its own.


set up new tunnel
~~~~~~~~~~~~~~~~~

Replacing *53419* with a number of your choosing, The port can’t be
*anything*. It needs to be between 1025 and 65535, and I recommend
49152–65535.

create the tunnel using :

.. code:: bash

   ssh -L 53419:localhost:3306 valinor.ucsf.edu

Note that after running it your shell is now on Valinor.

You will need to leave this tunnel open while connecting to Valar. As
long the terminal window connection is open, you can access valar
through your notebooks.

You can of course alias in your ``~/.shell-common``. Adding these lines
will provide a ``valinor-tunnel`` alias:

.. code:: bash

   export valinor_tunnel_port=53419
   alias valinor-tunnel='ssh -L ${valinor_tunnel_port}:localhost:3306 valinor.ucsf.edu'

This mode will allow you to use the same tunnel with other languages and
to connect to Valar natively. For example, you can connect to MariaDB
from a local terminal using:

.. code:: bash

   mysql -u dbusername -P $valinor_tunnel_port -p


Optional: choose to update your config file to randomize your tunnel port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you only use Python, this is slightly preferable because it
randomizes the tunnel port. That’s a very minor security benefit,
however. For this mode, just leave ``ssh_host: "valinor.ucsf.edu"``


simplest example
----------------

.. code:: python

   from valarpy.Valar import Valar

   with Valar():
   # you MUST import this AFTER setting global_connection.db
       from valarpy.model import *
       print("# of projects: {}".format(len(Projects.select())))

The sections below show more flexible usage.

example usage with Peewee
-------------------------

.. code:: python


   import valarpy.global_connection as global_connection

   def do_my_stuff():
       for row in Users.select():
           print(row.username)

   with global_connection.GlobalConnection.from_json('../config/real_config.json') as db:
       db.connect_with_peewee()     # don't worry, this will be closed with the GlobalConnection
       global_connection.db = db    # set a global variable, which peewee will access
       from valarpy.model import *  # you MUST import this AFTER setting global_connection.db
       do_my_stuff()

example usage with plain SQL
----------------------------

.. code:: python


   import valarpy.global_connection as global_connection

   def do_my_stuff():
       for row in db.select("SELECT username from users where first_name=%s", 'cole'):
           print(row)

   with global_connection.GlobalConnection.from_json('../config/real_config.json') as db:
       db.connect_with_raw_sql()
       global_connection.db = db    # you don't actually need to set this here
       do_my_stuff()

See `more examples <https://github.com/kokellab/kokel-scripts>`__ or the
`Peewee documentation <http://docs.peewee-orm.com/en/latest/>`__ for
further information.


running in Jupyter notebooks
----------------------------

Jupyter notebooks seem to drop the connection after the first cell. To
resolve this, you can avoid using a ``with`` statement by using:

.. code:: python

   db = global_connection.GlobalConnection.from_json('/home/dmyerstu/desktop/valar.json')
   db.open()
   db.connect_with_peewee()     # don't worry, this will be closed with the GlobalConnection
   global_connection.db = db    # set a global variable, which peewee will access
   from valarpy.model import *  # you MUST import this AFTER setting global_connection.db

   # do whatever till the end of the notebook

The database connection and SSH tunnels will hopefully be closed when
Jupyter exits. You can also close bith using ``db.close()``.


connecting from home
--------------------

The best way to use the database from home is to host a notebook server
on your work computer that you can view from any computer you wish.
`This
guide <http://jupyter-notebook.readthedocs.io/en/stable/public_server.html>`__
covers how to set this up.

`This is a general schematic of how this process works once set
up <https://github.com/kokellab/valar/blob/master/docs/jupyter-nb_server_overview.png>`__


notes about tables
------------------

Assay frames and features (such as MI) are stored as MySQL binary
``blob``\ s.

Each frame in ``assay_frames`` is represented as a single big-endian
unsigned byte. To convert back, use ``utils.blob_to_byte_array(blob)``,
where ``blob`` is the Python ``bytes`` object returned directly from the
database.

Each value in ``well_features`` (each value is a frame for features like
MI) is represented as 4 consecutive bytes that constitute a single
big-endian unsigned float (IEEE 754 ``binary32``). Use
``utils.blob_to_float_array(blob)`` to convert back.

There shouldn’t be a need to insert these data from Python, so there’s
no way to convert in the forwards direction.
