import itertools
from unittest.mock import patch

import pytest

# Makes the generated argument names predictable in the tests.
counter = itertools.count()
random_arg_name_patch = patch("lookup_property.typing.random_arg_name", side_effect=lambda: f"arg{next(counter)}")


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config: pytest.Config, parser: pytest.Parser, args: list[str]) -> None:
    random_arg_name_patch.start()
