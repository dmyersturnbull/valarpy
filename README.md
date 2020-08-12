# Valarpy

[![Version status](https://img.shields.io/pypi/status/valarpy)](https://pypi.org/project/valarpy/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/valarpy)](https://pypi.org/project/valarpy/)
[![Docker](https://img.shields.io/docker/v/dmyersturnbull/valarpy?color=green&label=DockerHub)](https://hub.docker.com/repository/docker/dmyersturnbull/valarpy)
[![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/dmyersturnbull/valarpy?include_prereleases&label=GitHub)](https://github.com/dmyersturnbull/valarpy/releases)
[![Latest version on PyPi](https://badge.fury.io/py/valarpy.svg)](https://pypi.org/project/valarpy/)
[![Documentation status](https://readthedocs.org/projects/valarpy/badge/?version=latest&style=flat-square)](https://valarpy.readthedocs.io/en/stable/)
[![Build & test](https://github.com/dmyersturnbull/valarpy/workflows/Build%20&%20test/badge.svg)](https://github.com/dmyersturnbull/valarpy/actions)

Python code to talk to [Valar](https://github.com/dmyersturnbull/valar).
There is more documentation available in the Valar readme.
[See the docs](https://valarpy.readthedocs.io/en/stable/).

Usage:

```python
from valarpy import *
with Valar():
    print(list(Refs.select()))
```

An example connection f=config file:

```json
{
  "local_bind_port": 53419,
  "ssh_port": 22,
  "db_username": "user",
  "db_password": "password",
  "db_port": 3306,
  "db_name": "valar"
}

```

[New issues](https://github.com/dmyersturnbull/valarpy/issues) and pull requests are welcome.
Please refer to the [contributing guide](https://github.com/dmyersturnbull/valarpy/blob/master/CONTRIBUTING.md).
Generated with [Tyrannosaurus](https://github.com/dmyersturnbull/tyrannosaurus).

