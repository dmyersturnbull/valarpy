import logging
import os
from pathlib import Path
from typing import Union

from pocketutils.misc.connection import Connection


class GLOBAL_CONNECTION:  # pragma: no cover
    db = None


def _get_existing_path(*paths):  # pragma: no cover
    paths = [None if p is None else Path(p) for p in paths]
    for path in paths:
        if path is not None and path.exists():
            return path


class Valar:
    """
    Simplest way to use valarpy with Peewee.
    Requires an environment variable named VALARPY_CONFIG that points to a JSON config file.
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
                Path.home() / ".valarpy" / "read_only.json",
            )
            if config_file_path is None or not config_file_path.is_file():
                raise FileNotFoundError(
                    "Path for VALARPY_CONFIG '{}' does not exist or is not a file.".format(
                        config_file_path
                    )
                )
        self.config_file_path = config_file_path

    def reconnect(self):
        self.close()
        self.open()

    def open(self) -> None:
        db = Connection.from_json(str(self.config_file_path))
        db.open()
        db.connect_with_peewee()  # don't worry, this will be closed with the Connection
        GLOBAL_CONNECTION.db = db  # set a global variable, which peewee will access

    def close(self) -> None:
        logging.info("Closing connection to Valar")
        GLOBAL_CONNECTION.db.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, t, value, traceback):
        self.close()

    def __del__(self):  # pragma: no cover
        self.close()


__all__ = ["GLOBAL_CONNECTION"]
