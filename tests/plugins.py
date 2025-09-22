import itertools
from unittest.mock import patch

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config: pytest.Config, parser: pytest.Parser, args: list[str]) -> None:
    counter = itertools.count()
    mock = patch("lookup_property.typing.random_arg_name", side_effect=lambda: f"arg{next(counter)}")
    mock.start()
