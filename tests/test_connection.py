import os

import pytest

from valarpy import *

CONFIG_PATH = Path(__file__).parent / "resources" / "connection.json"


class TestModel:
    def test_reconnect(self):
        with Valar(CONFIG_PATH) as valar:
            from valarpy.model import Refs

            assert list(Refs) is not None
            valar.reconnect()
            assert list(Refs) is not None

    def test_config_path(self):
        popped = None
        try:
            if "VALARPY_CONFIG" in os.environ:
                popped = os.environ.pop("VALARPY_CONFIG")
            with pytest.raises(LookupError):
                with Valar():
                    from valarpy.model import Refs

                    list(Refs.select())
            os.environ["VALARPY_CONFIG"] = str("asd346erfdgawq046j54e4y")
            with pytest.raises(FileNotFoundError):
                with Valar():
                    from valarpy.model import Refs

                    list(Refs.select())
            os.environ["VALARPY_CONFIG"] = str(CONFIG_PATH)
            with Valar():
                from valarpy.model import Refs

                assert list(Refs) is not None
        finally:
            if popped is not None:
                os.environ["VALARPY_CONFIG"] = popped


if __name__ == ["__main__"]:
    pytest.main()
