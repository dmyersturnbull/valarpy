import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Mapping, Union

import peewee

logger = logging.getLogger("valarpy")


class GlobalConnection:  # pragma: no cover
    peewee_database = None


class Valar:
    """
    Global valarpy connection.
    """

    def __init__(
        self,
        config: Union[
            None, str, Path, List[Union[str, Path, None]], Mapping[str, Union[str, int]]
        ] = None,
    ):
        """
        Constructor.

        Args:
            config: The connection info, which must contain "database" and optionally parameters passed to peewee
                If a dict, used as-is. If a path or str, attempts to read JSON from that path.
                If a list of paths, strs, and Nones, reads from the first extant file found in the list.
                If None, attempts to read JSON from the ``VALARPY_CONFIG`` environment variable, if set.

        Raises:
            FileNotFoundError: If a path was supplied but does not point to a file
            TypeError: If the type was not recognized
            InterfaceError: On some connection issues
        """
        if config is None:
            config = self._read_json(
                self.__class__.find_extant_path(os.environ.get("VALARPY_CONFIG"))
            )
        elif isinstance(config, (str, Path)):
            config = self._read_json(config)
        elif isinstance(config, list) and all(
            (isinstance(p, (str, Path)) for p in config if p is not None)
        ):
            config = self._read_json(self.__class__.find_extant_path(*config))
        elif (
            hasattr(config, "items")
            and hasattr(config, "values")
            and hasattr(config, "keys")
            and hasattr(config, "__getitem__")
            and hasattr(config, "get")
        ):
            pass
        else:
            raise TypeError(f"Invalid type {type(config)} of {config}")
        self._config: Dict[str, Union[str, int]] = config
        self._db_name = self._config.pop("database")

    @classmethod
    def find_extant_path(cls, *paths: Union[Path, str, None]) -> Path:
        """
        Finds the first extant path in the list.
        It is rare to need to call this directly.

        Args:
            *paths: A list of file paths; values of None are skipped

        Returns:
            The first Path that exists

        Raises:
            FileNotFoundError: If the path found is not a file
        """
        paths = [None if p is None else Path(p) for p in paths]
        path = None
        for path in paths:
            if path is not None and path.exists():
                return path
        if path is None:
            raise FileNotFoundError(f"File {path} not found")
        return path

    @classmethod
    def get_preferred_paths(cls) -> List[Path]:
        """
        Gets a list of preferred paths to look for config files, in order from highest-priority to least-priority.
        Starts with the ``VALARPY_CONFIG`` environment variable, if it is set.

        Returns: A list of ``Path`` instances
        """
        return [
            os.environ.get("VALARPY_CONFIG"),
            Path.home() / ".chemfish" / "connection.json",
            Path.home() / ".valarpy" / "connection.json",
            Path.home() / ".valarpy" / "config.json",
            Path.home() / ".valarpy" / "read_only.json",
        ]

    def reconnect(self) -> None:
        """
        Closes and then opens the connection.
        This may be useful for fixing connection issues.
        """
        self.close()
        self.open()

    def open(self) -> None:
        """
        Opens the database connection.
        This is already called by ``__enter__``.
        """
        logging.info(f"Opening connection to {self._db_name}")
        GlobalConnection.peewee_database = peewee.MySQLDatabase(self._db_name, **self._config)
        GlobalConnection.peewee_database.connect()

    def close(self) -> None:
        """
        Closes the connection.
        This is already called by ``__exit__``.
        """
        logging.info(f"Closing connection to {self._db_name}")
        GlobalConnection.peewee_database.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, t, value, traceback):
        self.close()

    def __del__(self):  # pragma: no cover
        self.close()

    @classmethod
    def _read_json(cls, path: Union[str, Path]) -> Dict[str, Any]:
        if not Path(path).exists():
            raise FileNotFoundError(f"JSON config file {path} does not exist")
        if not Path(path).is_file():
            raise FileNotFoundError(f"JSON config file {path} is not a file")
        return json.loads(Path(path).read_text(encoding="utf8"))


__all__ = ["GlobalConnection", "Valar"]
