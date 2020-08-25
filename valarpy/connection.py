import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Union

import peewee

logger = logging.getLogger("valarpy")


class GLOBAL_CONNECTION:  # pragma: no cover
    peewee_database = None


def _get_existing_path(*paths):  # pragma: no cover
    paths = [None if p is None else Path(p) for p in paths]
    for path in paths:
        if path is not None and path.exists():
            return path


class Valar:
    """
    Simplest way to use valarpy with Peewee.
    Ex:
        >>> with Valar():
        >>>	import valarpy.model as model
        >>>	print(len(model.Projects.select())
    """

    def __init__(self, config_file_path: Union[None, str, Path] = None):
        if config_file_path is None:
            if "VALARPY_CONFIG" not in os.environ:
                raise LookupError("Set VALARPY_CONFIG as an environment variable.")
            config_file_path = _get_existing_path(
                os.environ.get("VALARPY_CONFIG"),
                Path.home() / ".valarpy" / "config.json",
                Path.home() / ".valarpy" / "connection.json",
                Path.home() / ".valarpy" / "read_only.json",
            )
            if config_file_path is None or not config_file_path.is_file():
                raise FileNotFoundError(
                    f"Path for VALARPY_CONFIG '{config_file_path}' does not exist or is not a file."
                )
        self.config_file_path = config_file_path
        self._db_name = None

    def reconnect(self) -> None:
        self.close()
        self.open()

    def open(self) -> None:
        with open(self.config_file_path) as jscfg:
            params: Dict[str, Any] = json.load(jscfg)
        self._db_name = params.pop("database")
        logging.info(f"Opening connection to {self._db_name}")
        GLOBAL_CONNECTION.peewee_database = peewee.MySQLDatabase(self._db_name, **params)
        GLOBAL_CONNECTION.peewee_database.connect()

    def close(self) -> None:
        logging.info(f"Closing connection to {self._db_name}")
        GLOBAL_CONNECTION.peewee_database.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, t, value, traceback):
        self.close()

    def __del__(self):  # pragma: no cover
        self.close()


__all__ = ["GLOBAL_CONNECTION", "Valar"]
