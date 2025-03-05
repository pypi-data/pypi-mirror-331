import pytest

from opengenome.welcome import about


@pytest.fixture
def welcome_val() -> int:
    return 1


def test_welcome(welcome_val: int) -> None:
    assert welcome_val == about(), "Welcome did not return 1"
