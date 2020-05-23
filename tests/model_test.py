import pytest

from valarpy.model import *


class TestModel:

    def test_create(self):
        user = Users(username='hi', first_name='Hello', last_name='Hi')
        assert user.id is None


if __name__ == ['__main__']:
    pytest.main()
