# valarpy
Python code to talk to Valar / kokel-data. Import this into other projects.

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
