"""
Project metadata and convenience functions.
"""

import logging
from contextlib import contextmanager
from importlib.metadata import PackageNotFoundError
from importlib.metadata import metadata as __load
from pathlib import Path
from typing import Generator, List, Mapping, Union

import peewee

from valarpy.connection import Valar as __Valar

logger = logging.getLogger(Path(__file__).parent.name)

__metadata = None
try:
    __metadata = __load(Path(__file__).absolute().parent.name)
    __status__ = "Development"
    __copyright__ = "Copyright 2016–2020"
    __date__ = "2020-08-14"
    __uri__ = __metadata["home-page"]
    __title__ = __metadata["name"]
    __summary__ = __metadata["summary"]
    __license__ = __metadata["license"]
    __version__ = __metadata["version"]
    __author__ = __metadata["author"]
    __maintainer__ = __metadata["maintainer"]
    __contact__ = __metadata["maintainer"]
except PackageNotFoundError:  # pragma: no cover
    logger.error(
        "Could not load package __metadata for {}. Is it installed?".format(
            Path(__file__).absolute().parent.name
        )
    )


class Valar(__Valar):
    @classmethod
    def singleton(
        cls,
        config: Union[
            None, str, Path, List[Union[str, Path, None]], Mapping[str, Union[str, int]]
        ] = None,
    ):
        z = cls(config)
        return z


get_preferred_paths = Valar.get_preferred_paths


def new_model():
    """
    Shorthand for importing model.
    You should have a connection open.

    Returns:
        The ``model`` module
    """
    from valarpy import model

    return model


@contextmanager
def opened(
    config: Union[
        None, str, Path, List[Union[str, Path, None]], Mapping[str, Union[str, int]]
    ] = None
):
    """
    Context manager. Opens a connection and returns the model.
    Closes the connection when the generator exits.

    Args:
        config: Passed to ``Valar.__init__``

    Returns:
        The ``model`` module
    """
    with Valar(config):
        from valarpy import model

        yield model


def valarpy_info() -> Generator[str, None, None]:
    """
    Gets lines describing valarpy metadata and database row counts.
    Useful for verifying that the schema matches the valarpy model,
    and for printing info.

    Yields:
        Lines of free text

    Raises:
        InterfaceError: On some connection and schema mismatch errors
    """
    if __metadata is not None:
        yield "{} (v{})".format(__metadata["name"], __metadata["version"])
    else:
        yield "Unknown project info"
    yield "Connecting..."
    with opened(get_preferred_paths()) as m:
        yield "Connected."
        yield ""
        yield "Table                       N Rows"
        yield "----------------------------------"
        for sub in m.BaseModel.__subclasses__():
            count = sub.select(peewee.fn.COUNT(sub.id).alias("count")).first()
            yield f"{sub.__name__:<25} = {count.count}"
        yield "----------------------------------"
        yield ""
    yield "All valarpy queries succeeded."


if __name__ == "__main__":  # pragma: no cover
    for line in valarpy_info():
        print(line)


__all__ = ["Valar", "new_model", "opened", "valarpy_info", "get_preferred_paths"]
