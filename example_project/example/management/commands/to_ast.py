import ast
import json
from copy import deepcopy
from inspect import cleandoc
from typing import Any

from django.core.management import BaseCommand, CommandParser

to_convert = (
    ast.Attribute,
    ast.Name,
    ast.Call,
    ast.BinOp,
    ast.keyword,
    ast.arguments,
    ast.Constant,
    ast.Lambda,
    ast.FunctionDef,
    ast.Compare,
    ast.Subscript,
    ast.Slice,
    ast.UnaryOp,
    ast.USub,
    ast.UnaryOp,
    ast.Set,
    ast.IfExp,
)
to_remove = [
    "lineno",
    "col_offset",
    "end_col_offset",
    "end_lineno",
]


class Command(BaseCommand):
    help = "Parse a string into an AST repr. Useful for creating new converters."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("string")

    def handle(self, *args: Any, **options: Any) -> None:
        print_str_as_ast(options["string"])


def to_dict(tree: ast.AST) -> dict[str, Any]:
    value = deepcopy(tree.__dict__)

    for k, v in value.items():
        if isinstance(v, list):
            for i, item in enumerate(v):
                v[i] = to_dict(item)

        if isinstance(v, to_convert):
            value[k] = to_dict(v)

        elif isinstance(v, ast.AST):
            value[k] = f"ast.{v.__class__.__name__}"

    for key in to_remove:
        value.pop(key, None)

    value["__typename"] = f"ast.{tree.__class__.__name__}"
    return value


def get_source(value: str) -> ast.stmt:
    x = ast.parse(value).body[0]
    return getattr(x, "value", x)


def print_str_as_ast(input_string: str) -> None:
    source = get_source(cleandoc(input_string))
    data = to_dict(source)
    print("----------------------------------")  # noqa: T201, RUF100
    print(ast.unparse(source))  # noqa: T201, RUF100
    print("----------------------------------")  # noqa: T201, RUF100
    print(json.dumps(data, indent=2, sort_keys=True, default=str))  # noqa: T201, RUF100
    print("----------------------------------")  # noqa: T201, RUF100


if __name__ == "__main__":
    string = cleandoc(
        """
        self.__class__.objects.aggregate(random_string=random_string())["random_string"]
        """
    )
    print_str_as_ast(string)
