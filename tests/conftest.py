from functools import partial
from typing import Any, Callable, Generator

import pytest
from django.db import connection


def log_query(
    execute: Callable[..., Any],
    sql: str,
    params: tuple[Any, ...],
    many: bool,  # noqa: FBT001
    context: dict[str, Any],
    queries: list[str],
) -> Any:
    queries.append(sql % params)
    return execute(sql, params, many, context)


@pytest.fixture
def query_counter() -> Generator[list[str], None, None]:
    queries: list[str] = []
    func = partial(log_query, queries=queries)
    with connection.execute_wrapper(func):
        yield queries
