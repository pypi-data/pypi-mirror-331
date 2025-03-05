import pytest

from opengenome.welcome import about


@pytest.fixture
def welcome_val():
    return 1


def test_welcome(welcome_val):
    assert welcome_val == about(), "Welcome did not return 1"